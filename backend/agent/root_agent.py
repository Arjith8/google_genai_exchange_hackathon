from google.adk.agents import Agent

from agent.prompt.system.root_agent_prompt import ROOT_AGENT_SYSTEM_PROMPT


def root_agent() -> Agent:
    return Agent(
        name="demistify_agent",
        model="gemini-2.5-flash",
        description="Agent to answer questions about terms and conditions of services.",
        instruction=ROOT_AGENT_SYSTEM_PROMPT,
    )
