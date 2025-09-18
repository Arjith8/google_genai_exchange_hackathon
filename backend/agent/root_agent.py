from google.adk.agents import Agent

def root_agent() -> Agent: 
    return Agent(
        name="demistify-agent",
        model="gemini-2.5-flash",
        description="Agent to answer questions about terms and conditions of services.",
        instruction="""
        You are a helpful agent that can answer questions about terms and conditions of services.
        If user provides a URL, parse it.
        If no URL is provided, use Google Search to find the terms and conditions page url, then parse it.
        """,
    )
