from fastapi import FastAPI, Request
from agents.buyer_agent.agent import execute  # adjust import to your file structure
import asyncio

app = FastAPI()

@app.post("/run")
async def run_agent(request: Request):
    data = await request.json()
    result = await execute(data)
    return result
