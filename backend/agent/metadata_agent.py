from google.adk.agents import LlmAgent
from pydantic import BaseModel

class MetaData(BaseModel):
    product_name: str | None = None
    company_name: str | None = None

def metadata_agent() -> LlmAgent:
    return LlmAgent(
        name="metadata_agent",
        model="gemini-2.5-flash",
        description="Agent to extract metadata from HTML content.",
        instruction="""
        You are a helpful agent that can extract metadata from HTML content and return it in JSON format.
        Given the head section of an HTML document, you will extract information such as product_name and company_name if available.
        If the information is not available, return null for that field.
        """,
    )

