from google.adk.agents import Agent 
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner 
from google.adk.sessions import InMemorySessionService 
from google.genai import types 
import json 
import logging 

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Price Agent definition
price_agent = Agent(
    name="price_agent",
    model="gemini-2.0-flash",
    description="Estimates and compares property prices based on location, size, and property type.",
    instruction=(
        "Given property details (location, property type, and size in sq. ft), "
        "estimate the price range in INR and provide a short justification. "
        "For each property input, return:\n"
        "- Property type\n"
        "- Location\n"
        "- Size (sq. ft)\n"
        "- Estimated price range (min–max INR)\n"
        "- Justification (why this price range, e.g., demand, locality, market trends)\n"
        "Return the result strictly in JSON format with a 'price' array. "
        "Do not include extra text or markdown formatting."
    )
)


session_service = InMemorySessionService()
runner = Runner(
    agent=price_agent,
    app_name="price_app",
    session_service=session_service,
)

USER_ID = "user_price"
SESSION_ID = "session_price"

# Execute function
async def execute(request):
    logger.debug(f"Incoming request to price agent: {request}")
    
    # Create a session
    await session_service.create_session(
        app_name="price_app",
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    
    prompt = (
        f"Estimate the property price.\n"
        f"Location: {request.get('location', 'Not specified')}\n"
        f"Property Type: {request.get('property_type', 'Not specified')}\n"
        f"Size: {request.get('size', 'Not specified')} sq. ft\n"
        "Return as JSON with a 'price' array."
    )

    message = types.Content(role="user", parts=[types.Part(text=prompt)])

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=message
    ):
        if event.is_final_response():
            response_text = event.content.parts[0].text
            response_text = response_text.strip()
            
            # Clean response formatting
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Try parsing JSON
            try:
                parsed = json.loads(response_text)
                return {
                    "price": parsed.get("price", []),
                    "status": "success"
                }
            except json.JSONDecodeError:
                return {
                    "price": [],
                    "status": "error",
                    "message": "Failed to parse price data"
                }
