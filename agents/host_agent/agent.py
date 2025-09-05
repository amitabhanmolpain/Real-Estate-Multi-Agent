# agent.py
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# ---------------------------
# Define Host Agent
# ---------------------------
host_agent = Agent(
    name="host_agent",
    model="gemini-2.0-flash",
    description="Coordinates real estate planning by calling buyer, seller, price estimator, and neighborhood agents.",
    instruction=(
        "You are the Host Agent responsible for orchestrating real estate tasks. "
        "You call the buyer agent, seller agent, price estimator agent, and neighborhood agent. "
        "Your job is to collect their results and return a structured summary to the user."
    )
)

# ---------------------------
# Setup session + runner
# ---------------------------
session_service = InMemorySessionService()
runner = Runner(
    agent=host_agent,
    app_name="host_app",
    session_service=session_service
)

USER_ID = "user_host"
SESSION_ID = "session_host"

# ---------------------------
# Execution function
# ---------------------------
async def execute(request):
    # Ensure session exists
    await session_service.create_session(
        app_name="host_app",
        user_id=USER_ID,
        session_id=SESSION_ID
    )

    # Build prompt dynamically from request
    prompt = (
        f"Find real estate insights for the user.\n"
        f"Budget: {request.get('budget', 'Not specified')}\n"
        f"Preferred Location: {request.get('location', 'Not specified')}\n"
        f"Property Type: {request.get('property_type', 'Not specified')}\n\n"
        "Call the buyer agent, seller agent, price estimator agent, and neighborhood agent. "
        "Return a final structured summary combining all results."
    )

    # Send message to model
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
        if event.is_final_response():
            return {"summary": event.content.parts[0].text}
