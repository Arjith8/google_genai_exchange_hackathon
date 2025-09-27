import io
import json
import logging
import os
import re
import uuid

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.cloud import storage
from google.genai import types
from pydantic import BaseModel
import requests
from sqlalchemy import desc, select
from dotenv import load_dotenv

from agent import diff_agent, metadata_agent, root_agent
from database.client import create_db_session
from database.models import LinkMetadata
from utils.parse_html import HTMLParser


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logging.getLogger("google.adk").disabled = True


app = FastAPI()

session_service = InMemorySessionService()

load_dotenv()
GCP_BUCKET_NAME = os.getenv("GCP_BUCKET_NAME")
if not GCP_BUCKET_NAME:
    raise ValueError("GCP_BUCKET_NAME environment variable not set")

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
if not GCP_PROJECT_ID:
    raise ValueError("GCP_PROJECT_ID environment variable not set")

client = storage.Client(project=GCP_PROJECT_ID)
bucket = client.bucket(bucket_name=GCP_BUCKET_NAME)

origins = os.getenv("ORIGINS")
if not origins:
    raise ValueError("ORIGINS environment variable not set")
origins = origins.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_session = create_db_session()

@app.get("/")
def read_root():
    return {"Hello": origins}

class Chat(BaseModel):
    text: str
    session_id: str | None = None

@app.post("/chat")
async def chat(chat: Chat):
    session_id = chat.session_id
    if not session_id:
        session_id = str(uuid.uuid4())

    session = await session_service.get_session(
        user_id=session_id,
        session_id=session_id,
        app_name="demistify_agent"
    )
    print("Session fetched successfully", session)
    if not session:
        session = await session_service.create_session(
            user_id=session_id,
            session_id=session_id,
            app_name="demistify_agent"
        )
        print("Session created successfully", session)

    
    # Add test cases for this regex to be extra safe
    regex = r'https?:\/\/(?:localhost|\d{1,3}(?:\.\d{1,3}){3}|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})(?::\d+)?(?:[^\s]*)?'
    url = re.findall(regex, chat.text)
    extra_context = ""
    new_html_str = ""
    diff = ""
    if url:
        logging.info(f"URL found in user input: {url[0]}")
        stmt = (
            select(LinkMetadata)
            .where(LinkMetadata.url == url[0])
            .order_by(desc(LinkMetadata.created_at))
            .limit(1)
        )
        data = requests.get(url[0])
        new_html = HTMLParser.clean_html(data.text)

        header_content = HTMLParser.extract_header(new_html)
        header_content = header_content.prettify()
        new_html_str = new_html.prettify()

        result = db_session.execute(stmt).scalar_one_or_none()
        if not result:
            logging.info(f"No existing metadata found for URL: {url[0]}. Creating new entry.")
            logging.info(f"Extracting metadata using metadata_agent for URL: {url[0]}")
            agent = metadata_agent()

            metadata_agent_content = types.Content(role='user', parts=[types.Part(text=header_content)])
            metadata_agent_runner = Runner(agent=agent, app_name="demistify_agent", session_service=session_service)

            logging.info("Running metadata agent...")

            metadata_data = ""
            async for event in metadata_agent_runner.run_async(user_id=session_id, session_id=session_id, new_message=metadata_agent_content):
                if event.is_final_response() and event.content and event.content.parts:
                    metadata_data = event.content.parts[0].text

            if not metadata_data:
                metadata_data = "No final response received."

            logging.info(f"Metadata agent response: {metadata_data}")
            match = re.search(r"\{.*\}", metadata_data, re.DOTALL)
            metadata = {}
            if match:
                clean = match.group(0)
                metadata = json.loads(clean)

            # Need to figure out a better way using async efficiently, since I dont need to wait for this to finish I have 
            #   time till resp is send so i can check if there was some error or nah

            file = io.BytesIO(new_html_str.encode('utf-8'))
            blob_name = f"html/{uuid.uuid1()}.html"

            logging.info(f"Uploading HTML content to GCP bucket: {GCP_BUCKET_NAME}, blob: {blob_name}")

            blob = bucket.blob(blob_name)
            blob.upload_from_file(file, rewind=True, content_type="text/plain")

            logging.info(f"Upload complete. Storing metadata in database for URL: {url[0]}")

            # Need to check scope of using async with sqlalchemy
            logging.info(f"Metadata to be stored in DB: {metadata}")
            link_metadata = LinkMetadata(
                url=url[0],
                company_name=metadata.get("company_name"),
                product_name=metadata.get("product_name"),
                file_url=blob_name
            )
            db_session.add(link_metadata)
            db_session.commit()

            logging.info(f"Metadata stored successfully for URL: {url[0]}")

        else:
            logging.info(f"Existing metadata found for URL: {url[0]}. Checking for changes.")

            old_file_url = result.file_url

            logging.info(f"Fetching old HTML content from GCP bucket: {GCP_BUCKET_NAME}, blob: {old_file_url}")
            blob = bucket.blob(old_file_url)

            logging.info(f"Downloading old HTML content for comparison.")
            old_html = blob.download_as_text()

            logging.info(f"Comparing old and new HTML content.")
            diff = HTMLParser.diff_html(old_html, new_html)
            if diff:
                logging.info(f"Changes detected for URL: {url[0]}")

                logging.info(f"Extracting change summary using diff_agent.")
                diff_agent_instance = diff_agent()
                diff_agent_content = types.Content(role='user', parts=[types.Part(text=diff)])
                diff_agent_runner = Runner(agent=diff_agent_instance, app_name="demistify_agent", session_service=session_service)

                async for event in diff_agent_runner.run_async(user_id=session_id, session_id=session_id, new_message=diff_agent_content):
                    if event.is_final_response() and event.content and event.content.parts:
                        extra_context = event.content.parts[0].text

                logging.info(f"Change summary: {extra_context}")

        extra_context = extra_context

    combined_input = f"""
    [HTML Content From Link In User Question]
    {new_html_str if new_html_str else 'No HTML provided'}

    [Changes Summary]
    {extra_context}

    [User Question]
    {chat.text}
    """

    # Build ADK content
    user_content = types.Content(role="user", parts=[types.Part(text=combined_input)])

    # Run against your main agent (could be metadata_agent or another)
    main_agent = root_agent()
    main_runner = Runner(agent=main_agent, app_name="demistify_agent", session_service=session_service)

    final_response = ""
    async for event in main_runner.run_async(
        user_id=session_id,
        session_id=session_id,
        new_message=user_content
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_response = event.content.parts[0].text

    if not final_response:
        final_response = "No final response received."

    return {
        "data": {
            "response": final_response,
            "session_id": session_id,
            "diff": diff
        }
    }
