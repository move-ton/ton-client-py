import unittest
import logging
import asyncio
import random
import base64
from datetime import datetime
from typing import Dict, Any

from tonclient.bindings.types import TCResponseType
from tonclient.client import TonClient, DEVNET_BASE_URL
from tonclient.types import AppRequestResult, ParamsOfAppSigningBox, \
    ResultOfAppSigningBox


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

    def test_signing_box(self):
        storage: Dict[str, Any] = {
            'internal_keys': None,
            'internal_signature': None,
            'keys_handle': None,
            'external_handle': None
        }

        async def __main():
            await asyncio.gather(__coro_box_external(), __coro_box())

        async def __coro_box_external():
            storage['internal_keys'] = \
                await self.client.crypto.generate_random_sign_keys()
            storage['keys_handle'] = await self.client.crypto.get_signing_box(
                keypair=storage['internal_keys'])

            async for event in self.client.crypto.register_signing_box():
                data = event['response_data']
                if not data:
                    continue

                if event['response_type'] == TCResponseType.Success:
                    storage['external_handle'] = data['handle']
                if event['response_type'] == TCResponseType.AppRequest:
                    params = ParamsOfAppSigningBox.from_dict(
                        data=data['request_data'])
                    result = None

                    if isinstance(params, ParamsOfAppSigningBox.GetPublicKey):
                        public = await self.client.crypto.signing_box_get_public_key(
                            handle=storage['keys_handle'])
                        result = ResultOfAppSigningBox.GetPublicKey(
                            public_key=public)
                    if isinstance(params, ParamsOfAppSigningBox.Sign):
                        storage['internal_signature'] = \
                            await self.client.crypto.signing_box_sign(
                                signing_box=storage['keys_handle'],
                                unsigned=params.unsigned)
                        result = ResultOfAppSigningBox.Sign(
                            signature=storage['internal_signature'])

                    result = AppRequestResult.Ok(result=result.dict)
                    await self.client.resolve_app_request(
                        app_request_id=data['app_request_id'], result=result)

        async def __coro_box():
            while True:
                if storage.get('external_handle') is not None:
                    break
                await asyncio.sleep(1)

            public = await self.client.crypto.signing_box_get_public_key(
                handle=storage['external_handle'])
            self.assertEqual(storage['internal_keys'].public, public)

            signature = await self.client.crypto.signing_box_sign(
                signing_box=storage['external_handle'],
                unsigned=base64.b64encode(b'Test'))
            self.assertEqual(storage['internal_signature'], signature)

            await self.client.crypto.remove_signing_box(
                handle=storage['external_handle'])
            await self.client.crypto.remove_signing_box(
                handle=storage['keys_handle'])

        asyncio.get_event_loop().run_until_complete(__main())

    async def _coro_subscription(self):
        now = int(datetime.now().timestamp())
        generator = self.client.net.subscribe_collection(
            collection='messages', filter={'created_at': {'gt': now}},
            result='created_at')
        handle = None
        results = []
        async for response in generator:
            logging.info(f'[Subscribe coro] {response}')
            results.append(response)
            data = response['response_data']
            if not data:
                continue

            if response['response_type'] == TCResponseType.Success:
                handle = data['handle']

            if (int(datetime.now().timestamp()) > now + 7 or
                    response['response_type'] > TCResponseType.Custom) and \
                    handle:
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
