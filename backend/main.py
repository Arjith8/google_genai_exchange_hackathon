import io
import json
import logging
import os
import re
from typing import Optional
import uuid

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.cloud import storage
from google.genai import types
from pydantic import BaseModel
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from dotenv import load_dotenv

from agent import metadata_agent
from utils.parse_html import HTMLParser

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)

app = FastAPI()

engine = create_engine('sqlite:///test.db', echo=True)
class Base(DeclarativeBase):
    pass

class LinkMetadata(Base):
    __tablename__ = 'link_metadata'
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str]
    company_name: Mapped[Optional[str]] = mapped_column(nullable=True)
    product_name: Mapped[Optional[str]] = mapped_column(nullable=True)
    file_url: Mapped[Optional[str]] = mapped_column(nullable=False)

Base.metadata.create_all(engine)

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
session_service = InMemorySessionService()

load_dotenv()
GCP_BUCKET_NAME = os.getenv("GCP_BUCKET_NAME")
if not GCP_BUCKET_NAME:
    raise ValueError("GCP_BUCKET_NAME environment variable not set")

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
if not GCP_PROJECT_ID:
    raise ValueError("GCP_PROJECT_ID environment variable not set")

@app.get("/")
def read_root():
    return {"Hello": "World"}

class Chat(BaseModel):
    text: str
    session_id: str | None = None

@app.post("/chat")
async def chat(chat: Chat):
    session_id = chat.session_id
    if not session_id:
        session_id = str(uuid.uuid4())

    # Add test cases for this regex to be extra safe
    regex = r'https?:\/\/[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:[^\s]*)?'
    url = re.findall(regex, chat.text)
    if url:
        data = requests.get(url[0])

        data = HTMLParser.clean_html(data.text)

        header_content = HTMLParser.extract_header(data)
        header_content = header_content.prettify()

        agent = metadata_agent()

        metadata_agent_content = types.Content(role='user', parts=[types.Part(text=header_content)])
        session = await session_service.create_session(app_name="metadata_agent", user_id=session_id, session_id=session_id)
        metadata_agent_runner = Runner(agent=agent, app_name="metadata_agent", session_service=session_service)

        final_response_content = ""
        async for event in metadata_agent_runner.run_async(user_id=session_id, session_id=session_id, new_message=metadata_agent_content):
            if event.is_final_response() and event.content and event.content.parts:
                final_response_content = event.content.parts[0].text

        if not final_response_content:
            final_response_content = "No final response received."

        match = re.search(r"\{.*\}", final_response_content, re.DOTALL)
        metadata = {}
        if match:
            clean = match.group(0)
            metadata = json.loads(clean)

        # Need to figure out a better way using async efficiently, since I dont need to wait for this to finish I have 
        #   time till resp is send so i can check if there was some error or nah
        data = data.prettify()
        file = io.BytesIO(data.encode('utf-8'))
        blob_name = f"html/{session_id}.html"
        client = storage.Client(project=GCP_PROJECT_ID)
        bucket = client.bucket(bucket_name=GCP_BUCKET_NAME)
        blob = bucket.blob(blob_name)
        blob.upload_from_file(file, rewind=True, content_type="text/plain")

        # Need to check scope of using async with sqlalchemy
        with Session(engine) as session:
            link_metadata = LinkMetadata(
                url=url[0],
                company_name=metadata.get("company_name"),
                product_name=metadata.get("product_name"),
                file_url=blob_name
            )
            session.add(link_metadata)
            session.commit()

        # Do the diff check then send all context to the root agent
        return {"response": f"URL detected: {url[0]}", "metadata": data}

    content = types.Content(role='user', parts=[types.Part(text=chat.text)])
    return {
        "data": {
            "response": "No URL detected in the input text.",
            "session_id": session_id,
        }
    }
