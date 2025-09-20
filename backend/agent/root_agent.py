from google.adk.agents import Agent

def root_agent() -> Agent: 
    return Agent(
        name="demistify_agent",
        model="gemini-2.5-flash",
        description="Agent to answer questions about terms and conditions of services.",
        instruction="""
        You are a helpful agent that can answer questions about terms and conditions of services.
        If a user provides url a parsed html context will be provided to you.
        If its not the first time url was provided, you will also get a summary of changes that happened since last time this information.
        This changes information should be provided in the end of your answer with > ⚠️ Notice: <summary of changes>.
        """,
    )
