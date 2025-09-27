from google.adk.agents import LlmAgent
from pydantic import BaseModel

from agent.prompt.system.metadata_agent_prompt import METADATA_AGENT_SYSTEM_PROMPT

class MetaData(BaseModel):
    product_name: str | None = None
    company_name: str | None = None

def metadata_agent() -> LlmAgent:
    return LlmAgent(
        name="metadata_agent",
        model="gemini-2.5-flash",
        description="Agent to extract metadata from HTML content.",
        instruction=METADATA_AGENT_SYSTEM_PROMPT,
    )

