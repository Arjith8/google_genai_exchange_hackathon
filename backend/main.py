import re
from typing import Union

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid

app = FastAPI()

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

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


class Chat(BaseModel):
    text: str
    session_id: str | None = None

@app.post("/chat")
def chat(chat: Chat):
    session_id = chat.session_id
    if not session_id:
        session_id = str(uuid.uuid4())

    # Add test cases for this regex to be extra safe
    print(session_id)
    regex = r'https?:\/\/[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:[^\s]*)?'
    url = re.findall(regex, chat.text)
    if url:
        return {"response": f"URL detected: {url[0]}"}

    return {
        "data": {
            "response": "No URL detected in the input text.",
            "session_id": session_id
        }
    }
