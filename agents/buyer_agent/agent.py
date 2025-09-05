# agent.py
import json
import logging
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# --- Agent definition ---
buyer_agent = Agent(
    name="buyer_agent",
    model="gemini-2.0-flash",
    description=(
        "Helps buyers find and evaluate real estate properties "
        "based on their preferences, location, and budget."
    ),
    instruction=(
        "Given a buyer’s preferences (location, budget, property type, and key requirements), "
        "suggest 2–3 suitable property options. "
        "Return ONLY valid JSON in the following format:\n"
        "{ \"buyer\": [ { \"name\": \"...\", \"description\": \"...\", \"price\": 0, "
        "\"location\": \"...\", \"size\": 0, \"features\": [\"...\"] } ] }\n"
        "Do not include any extra text, markdown, or code fences."
    )
)

# --- Session + Runner ---
session_service = InMemorySessionService()
runner = Runner(
    agent=buyer_agent,
    app_name="buyer_app",
    session_service=session_service,
)

USER_ID = "user_buyer"
SESSION_ID = "session_buyer"


# --- Execution function ---
async def execute(request: dict):
    """
    Runs the buyer agent with the given request dict.
    Expected keys: location, budget, property_type, requirements
    """
    logger.debug(f"Incoming request to buyer agent: {request}")

    # Ensure session exists
    await session_service.create_session(
        app_name="buyer_app",
        user_id=USER_ID,
        session_id=SESSION_ID
    )

    # Build prompt
    prompt = (
        f"Suggest real estate properties for a buyer.\n"
        f"Location: {request.get('location', 'Not specified')}\n"
        f"Budget: {request.get('budget', 'Not specified')}\n"
        f"Property Type: {request.get('property_type', 'Not specified')}\n"
        f"Requirements: {request.get('requirements', 'None')}\n"
        "Return ONLY valid JSON with a 'buyer' array."
    )

    message = types.Content(role="user", parts=[types.Part(text=prompt)])

    found_final = False
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=message
    ):
        if event.is_final_response():
            found_final = True
            response_text = event.content.parts[0].text.strip()
            logger.debug(f"Raw model output: {response_text}")

            # Strip code fences if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

            try:
                parsed = json.loads(response_text)
                return {"buyer": parsed.get("buyer", []), "status": "success"}
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error: {e}")
                return {
                    "buyer": [],
                    "status": "error",
                    "message": "Failed to parse buyer data"
                }

    if not found_final:
        logger.error("No final response from agent")
        return {
            "buyer": [],
            "status": "error",
            "message": "No final response from agent"
        }
