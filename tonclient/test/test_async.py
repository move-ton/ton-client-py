import unittest
import logging
import asyncio
import random
from datetime import datetime

from tonclient.client import TonClient, DEVNET_BASE_URL
from tonclient.net import TonQLQuery


class TestTonClientAsync(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TonClient(
            network={'server_address': DEVNET_BASE_URL}, is_async=True)

    def test_gathering(self):
        async def __main():
            subscribe_results, mnemonics, keypairs = await asyncio.gather(
                self._coro_subscription(), self._coro_mnemonics(),
                self._coro_keypairs())
            self.assertGreater(len(subscribe_results), 0)
            self.assertEqual(7, len(mnemonics))
            self.assertEqual(10, len(keypairs))

        asyncio.get_event_loop().run_until_complete(__main())

    async def _coro_subscription(self):
        now = int(datetime.now().timestamp())
        query = TonQLQuery(collection='messages') \
            .set_filter(created_at__gt=now).set_result('created_at')
        generator = self.client.net.subscribe_collection(query=query)
        handle = None
        results = []
        async for response in generator:
            logging.info(f'[Subscribe coro] {response}')
            results.append(response)
            if response['response_data'].get('handle'):
                handle = response['response_data']['handle']

            if (int(datetime.now().timestamp()) > now + 7 or
                    response['response_type'] > 100) and handle:
                await self.client.net.unsubscribe(handle=handle)
                handle = None
        return results

    async def _coro_mnemonics(self):
        mnemonics = []
        while len(mnemonics) < 7:
            mnemonic = await self.client.crypto.mnemonic_from_random()
            mnemonics.append(mnemonic)
            logging.info(f'[Mnemonic coro] {mnemonic}')
            await asyncio.sleep(random.randint(1, 3))
        return mnemonics

    async def _coro_keypairs(self):
        keypairs = []
        while len(keypairs) < 10:
            keypair = await self.client.crypto.generate_random_sign_keys()
            keypairs.append(keypair)
            logging.info(f'[Keypair coro] {keypair.public}')
            await asyncio.sleep(1)
        return keypairs
