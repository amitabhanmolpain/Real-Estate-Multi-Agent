import asyncio
from agents.neighborhood_agent.agent import execute  # absolute import is safer

async def run(payload: dict):
    return await execute(payload)

# Optional: allow running standalone for testing
if __name__ == "__main__":
    test_payload = {"location": "Bengaluru", "requirements": "Good schools"}
    result = asyncio.run(run(test_payload))
    print(result)
