import json
import os
import re
from typing import Optional, Union
import certifi
import requests

from google.genai import types
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from agent import metadata_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

import logging

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

print(os.environ.get("SSL_CERT_FILE"), certifi.where())
print(os.environ.get("SSL_CERT_DIR"))

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

        final_response_content = "No final response received."
        async for event in metadata_agent_runner.run_async(user_id=session_id, session_id=session_id, new_message=metadata_agent_content):
            if event.is_final_response() and event.content and event.content.parts:
                final_response_content = event.content.parts[0].text

        if not final_response_content:
            final_response_content = "No final response received."

        match = re.search(r"\{.*\}", final_response_content, re.DOTALL)
        if match:
            clean = match.group(0)
            data = json.loads(clean)

        with Session(engine) as session:
            link_metadata = LinkMetadata(
                url=url[0],
                company_name=data.get("company_name"),
                product_name=data.get("product_name")
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
