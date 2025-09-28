from playwright.sync_api import sync_playwright
from fastapi import FastAPI

from utils.parse_html import HTMLParser
from pydantic import AnyUrl, BaseModel, EmailStr

app = FastAPI()

class Link(BaseModel):
    link: AnyUrl

@app.post("/")
def clean_html(body: Link):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(str(body.link))
        content = page.content()
        content = HTMLParser.clean_html(content).prettify()

        return {"content": str(content)}
