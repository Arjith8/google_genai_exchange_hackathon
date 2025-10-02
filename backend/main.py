import logging
import os
import re
import uuid

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.cloud import storage
from google.genai import types
from pydantic import BaseModel
from sqlalchemy import desc, select

from agent import diff_agent, root_agent
from database.client import create_db_session
from database.models import LinkMetadata
from utils.chat import ChatUtils
from utils.file import FileUtils
from utils.metadata import MetadataUtils
from utils.parse_html import HTMLParser

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
logging.getLogger("google.adk").disabled = True

logger = logging.getLogger(__name__)


app = FastAPI()

chat_utils = ChatUtils(InMemorySessionService())
session_service = chat_utils.session_service

load_dotenv()
GCP_BUCKET_NAME = os.getenv("GCP_BUCKET_NAME")
if not GCP_BUCKET_NAME:
    msg = "GCP_BUCKET_NAME environment variable not set"
    raise ValueError(msg)

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
if not GCP_PROJECT_ID:
    msg = "GCP_PROJECT_ID environment variable not set"
    raise ValueError(msg)

client = storage.Client(project=GCP_PROJECT_ID)
bucket = client.bucket(bucket_name=GCP_BUCKET_NAME)

origins = os.getenv("ORIGINS")
if not origins:
    msg = "ORIGINS environment variable not set"
    raise ValueError(msg)

origins = origins.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_session = create_db_session()


class RootResponse(BaseModel):
    status: str


@app.get("/", response_model=RootResponse)
def status() -> RootResponse:
    """
    Return the API status.
    """
    return RootResponse(status="OK")


class ChatRequest(BaseModel):
    text: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    data: dict


@app.post("/chat")
async def chat(chat: ChatRequest) -> ChatResponse:
    """
    Chat endpoint.
    """
    session_id = await chat_utils.get_or_create_session_id(chat.session_id)

    # Add test cases for this regex to be extra safe
    regex = r"https?:\/\/(?:localhost|\d{1,3}(?:\.\d{1,3}){3}|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})(?::\d+)?(?:[^\s]*)?"
    url = re.findall(regex, chat.text)
    extra_context = ""
    new_html_str = ""
    diff = ""
    if url:
        logger.info("URL found in user input: %s", url[0])
        stmt = select(LinkMetadata).where(LinkMetadata.url == url[0]).order_by(desc(LinkMetadata.created_at)).limit(1)
        new_html = HTMLParser.clean_html(url[0])

        header_content = HTMLParser.extract_header(new_html)
        header_content = header_content.prettify()
        new_html_str = new_html.prettify()

        result = db_session.execute(stmt).scalar_one_or_none()
        if not result:
            metadata = await MetadataUtils.extract_metadata(
                header_content=header_content, session_id=session_id, session_service=session_service
            )

            # Need to figure out a better way using async efficiently, since I dont need to wait for this to finish
            # I have time till resp is send so i can check if there was some error or nah
            file_name = f"html/{uuid.uuid1()}.html"
            FileUtils.upload(file=new_html_str, file_name=file_name, bucket=bucket)

            logger.info("Upload complete. Storing metadata in database for URL: %s", url[0])

            # Need to check scope of using async with sqlalchemy
            link_metadata = LinkMetadata(
                url=url[0],
                company_name=metadata.get("company_name"),
                product_name=metadata.get("product_name"),
                file_url=file_name,
            )
            db_session.add(link_metadata)
            db_session.commit()

            logger.info("Metadata stored successfully")

        else:
            logger.info("Existing metadata found for URL: %s. Checking for changes.", url[0])

            old_file_url = result.file_url

            logger.info("Fetching old HTML content from GCP bucket")
            blob = bucket.blob(old_file_url)

            logger.info("Downloading old HTML content for comparison.")
            old_html = blob.download_as_text()

            logger.info("Comparing old and new HTML content.")
            diff = HTMLParser.diff_html(old_html, new_html)
            if diff:
                logger.info("Extracting change summary using diff_agent.")
                diff_agent_instance = diff_agent()
                diff_agent_content = types.Content(role="user", parts=[types.Part(text=diff)])
                diff_agent_runner = Runner(
                    agent=diff_agent_instance, app_name="demistify_agent", session_service=session_service
                )

                async for event in diff_agent_runner.run_async(
                    user_id=session_id, session_id=session_id, new_message=diff_agent_content
                ):
                    if event.is_final_response() and event.content and event.content.parts:
                        extra_context = event.content.parts[0].text

    combined_input = f"""
    [HTML Content From Link In User Question]
    {new_html_str if new_html_str else "No HTML provided"}

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
    async for event in main_runner.run_async(user_id=session_id, session_id=session_id, new_message=user_content):
        if event.is_final_response() and event.content and event.content.parts:
            final_response = event.content.parts[0].text

    if not final_response:
        final_response = "No final response received."

    return {"data": {"response": final_response, "session_id": session_id, "diff": diff}}
