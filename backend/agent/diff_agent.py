from google.adk.agents import Agent

from agent.prompt.system.diff_agent_prompt import DIFF_AGENT_SYSTEM_PROMPT


def diff_agent() -> Agent:
    return Agent(
        name="diff_agent",
        model="gemini-2.5-flash",
        description="Agent that highlights differences between past and current versions of a terms page.",
        instruction=DIFF_AGENT_SYSTEM_PROMPT,
    )
