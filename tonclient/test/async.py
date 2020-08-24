import asyncio
import logging

from tonclient.client import TonClient, DEVNET_BASE_URL

logger = logging.getLogger("TONAsyncTests")
client = TonClient(servers=[DEVNET_BASE_URL])  # Default sync client


async def coro():
    return await client.crypto.ed25519_keypair()


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
        asyncio.wait(fs=[
            client.version(),
            client.crypto.random_generate_bytes(length=8),
            client.crypto.mnemonic_derive_sign_keys(mnemonic="machine logic master small before pole ramp ankle stage trash pepper success oxygen unhappy engine muscle party oblige situate cement fame keep inform lemon"),
            client.crypto.mnemonic_from_random(word_count=12),
            client.crypto.mnemonic_verify(mnemonic="bad"),
            client.crypto.ton_crc16(string_fmt={"text": "Test"}),
            client.crypto.factorize(number="2a"),
            client.crypto.nacl_box_keypair(),
            client.crypto.nacl_box_keypair_from_secret_key(secret_key="7ee962326304f9f88d5048fabdde7921411b1aad6400ef984c85a0a9cb3b1a7c")
        ]))
    for task in finished:
        logger.warning(f"Multiple async requests result: {task.result()}")
