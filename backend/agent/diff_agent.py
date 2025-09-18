from google.adk.agents import Agent


def diff_agent() -> Agent:
    return Agent(
        name="diff-agent",
        model="gemini-2.5-flash",
        description="Agent that highlights differences between past and current versions of a terms page.",
        instruction="""
        You are a helpful agent responsible for comparing two versions of 2 html files whose diff will be provided to you and returning a summary of what has changed.
        """,
    )

