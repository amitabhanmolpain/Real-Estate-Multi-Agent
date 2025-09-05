from fastapi import FastAPI, Request
import uvicorn
from .price_agent import execute

app = FastAPI()

@app.post("/run")
async def run_price_agent(request: Request):
    payload = await request.json()
    return await execute(payload)

if __name__ == "__main__":
    uvicorn.run("agents.price_agent.__main__:app", host="127.0.0.1", port=8003, reload=True)
