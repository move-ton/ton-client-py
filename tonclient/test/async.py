import asyncio
import logging

from tonclient.client import TonClient, DEVNET_BASE_URL

logger = logging.getLogger("TONAsyncTests")
client = TonClient(servers=[DEVNET_BASE_URL])  # Default sync client


async def coro():
    return await client.version()


if __name__ == "__main__":
    # Default sync request
    version = client.version()
    logger.warning(f"Sync request: {version}")

    # Set client to async mode
    client.is_async = True

    # Single async request
    version = asyncio.run(coro())
    logger.warning(f"Single async request: {version}")

    # Multiple async requests
    finished, unfinished = asyncio.run(
        asyncio.wait([client.version() for _ in range(50)]))
    for task in finished:
        logger.warning(f"Multiple async request result: {task.result()}")
