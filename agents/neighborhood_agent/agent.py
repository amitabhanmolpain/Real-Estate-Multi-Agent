from fastapi import FastAPI, Request
import uvicorn
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

neighborhood_agent = Agent(
    name="neighborhood_agent",
    model="gemini-2.0-flash",
    description="Provides detailed neighborhood insights such as safety, schools, amenities, transportation, and lifestyle based on the buyer's preferred location.",
    instruction=(
        "Given a neighborhood location, provide insights about:\n"
        "- Area name\n"
        "- Safety rating (1–5)\n"
        "- Nearby schools and ratings\n"
        "- Key amenities (hospitals, malls, grocery stores, parks, gyms, etc.)\n"
        "- Transportation & connectivity\n"
        "- Lifestyle & community description\n"
        "Return the result strictly in JSON format with a 'neighborhood' array. "
        "Do not include extra text or markdown formatting."
    )
)

session_service = InMemorySessionService()
runner = Runner(
    agent=neighborhood_agent,
    app_name="neighborhood_app",
    session_service=session_service,
)

USER_ID = "user_neighborhood"
SESSION_ID = "session_neighborhood"

async def execute(request):
    logger.debug(f"Incoming request to neighborhood agent: {request}")
    await session_service.create_session(
        app_name="neighborhood_app",
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    prompt = (
        f"Provide neighborhood insights.\n"
        f"Location: {request.get('location', 'Not specified')}\n"
        f"Requirements: {request.get('requirements', 'None')}\n"
        "Return as JSON with a 'neighborhood' array."
    )
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=message
    ):
        if event.is_final_response():
            response_text = event.content.parts[0].text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            try:
                parsed = json.loads(response_text)
                return {
                    "neighborhood": parsed.get("neighborhood", []),
                    "status": "success"
                }
            except json.JSONDecodeError:
                return {
                    "neighborhood": [],
                    "status": "error",
                    "message": "Failed to parse neighborhood data"
                }

app = FastAPI()

@app.post("/run")
async def run_agent(request: Request):
    data = await request.json()
    return await execute(data)

if __name__ == "__main__":
    uvicorn.run("agents.neighborhood_agent.agent:app", host="127.0.0.1", port=8004, reload=True)
