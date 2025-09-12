from google.adk.agents import Agent


diff_agent = Agent(
    name="diff-agent",
    model="gemini-2.5-flash",
    description="Agent that highlights differences between past and current versions of a terms page.",
    instruction="""
    You are responsible for comparing two versions of a terms of service page and 
    returning a summary of what has changed.
    """,
    tools=[],
)

