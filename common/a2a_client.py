from httpx import AsyncClient, TimeoutException
import logging
import asyncio

TIMEOUT_SECONDS = 30
MAX_RETRIES = 3
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
async def call_agent(url, payload, timeout=TIMEOUT_SECONDS, retries=MAX_RETRIES):
    async with AsyncClient() as client:
        for attempt in range(retries):
            try:
                response = await client.post(url, json=payload, timeout=timeout)
                response.raise_for_status()
                return response.json()
            except TimeoutException:
                logger.warning(f"Timeout on attempt {attempt + 1} for {url}")
                if attempt == retries - 1:
                    return {}
            except Exception as e:
                logger.error(f"Error calling {url}: {str(e)}")
                if attempt == retries - 1:
                    return {}
            await asyncio.sleep(1)  