import base64
import unittest
import logging
import asyncio
from datetime import datetime

from tonclient.client import TonClient, DEVNET_BASE_URLS
from tonclient.errors import TonException
from tonclient.objects import AppSigningBox, AppEncryptionBox
from tonclient.types import ClientConfig, ParamsOfMnemonicFromRandom, \
    ParamsOfAppRequest, ParamsOfAppSigningBox, ResultOfAppSigningBox, \
    ParamsOfSigningBoxSign, AppRequestResult, ParamsOfResolveAppRequest, \
    ParamsOfSign, ParamsOfParse, SubscriptionResponseType, \
    ResultOfSubscription, ClientError, ParamsOfSubscribeCollection, \
    ParamsOfConvertAddress, AddressStringFormat, ParamsOfRunExecutor, \
    AccountForExecutor, ParamsOfEncryptionBoxGetInfo, \
    ParamsOfEncryptionBoxEncrypt, ParamsOfEncryptionBoxDecrypt, \
    EncryptionBoxInfo, ParamsOfAppEncryptionBox

from tonclient.test.test_client import LIB_VERSION


class TestTonClientAsync(unittest.TestCase):
    def setUp(self) -> None:
        client_config = ClientConfig()
        client_config.network.endpoints = DEVNET_BASE_URLS
        self.client = TonClient(config=client_config, is_async=True)

    def test_version(self):  # Client
        async def __main():
            result = await self.client.version()
            self.assertEqual(LIB_VERSION, result.version)

        asyncio.run(__main())

    def test_gathering(self):  # Some modules
        async def __main():
            mnemonics, keypairs = await asyncio.gather(
                __coro_mnemonics(), __coro_keypairs())
            self.assertEqual(10, len(mnemonics))
            self.assertEqual(10, len(keypairs))

        async def __coro_mnemonics():
            mnemonics = []
            while len(mnemonics) < 10:
                params = ParamsOfMnemonicFromRandom()
                mnemonic = await self.client.crypto.mnemonic_from_random(
                    params=params)
                mnemonics.append(mnemonic)
                logging.info(f'[Mnemonic coro] {mnemonic.phrase}')
            return mnemonics

        async def __coro_keypairs():
            keypairs = []
            while len(keypairs) < 10:
                keypair = await self.client.crypto.generate_random_sign_keys()
                keypairs.append(keypair)
                logging.info(f'[Keypair coro] {keypair.public}')
            return keypairs

        asyncio.run(__main())

    def test_register_signing_box(self):  # Crypto
        async def __main():
            keys = await self.client.crypto.generate_random_sign_keys()
            keys_box_handle = await self.client.crypto.get_signing_box(
                params=keys)

            def __callback(response_data, _, loop):
                request = ParamsOfAppRequest(**response_data)
                box_params = ParamsOfAppSigningBox.from_dict(
                    data=request.request_data)
                box_result = None

                if isinstance(box_params, ParamsOfAppSigningBox.GetPublicKey):
                    # Run thread safe coroutine and wait for result
                    future = self.client.crypto.signing_box_get_public_key(
                        params=keys_box_handle)
                    future = asyncio.run_coroutine_threadsafe(
                        coro=future, loop=loop)
                    _result = future.result()

                    # Resolve params
                    box_result = ResultOfAppSigningBox.GetPublicKey(
                        public_key=_result.pubkey)
                if isinstance(box_params, ParamsOfAppSigningBox.Sign):
                    # Run thread safe coroutine and wait for result
                    params = ParamsOfSigningBoxSign(
                        signing_box=keys_box_handle.handle,
                        unsigned=box_params.unsigned)
                    future = self.client.crypto.signing_box_sign(params=params)
                    future = asyncio.run_coroutine_threadsafe(
                        coro=future, loop=loop)
                    _result = future.result()

                    # Resolve params
                    box_result = ResultOfAppSigningBox.Sign(
                        signature=_result.signature)

                # Create resolve app request params
                request_result = AppRequestResult.Ok(
                    result=box_result.dict)
                resolve_params = ParamsOfResolveAppRequest(
                    app_request_id=request.app_request_id,
                    result=request_result)

                future = self.client.resolve_app_request(params=resolve_params)
                future = asyncio.run_coroutine_threadsafe(
                    coro=future, loop=loop)
                future.result()

            # Get external signing box
            external_box = await self.client.crypto.register_signing_box(
                callback=__callback)

            # Request box public key
            box_pubkey = await self.client.crypto.signing_box_get_public_key(
                params=external_box)
            self.assertEqual(keys.public, box_pubkey.pubkey)

            # Get signature from signing box
            unsigned = base64.b64encode(b'Test Message').decode()
            sign_params = ParamsOfSigningBoxSign(
                signing_box=external_box.handle, unsigned=unsigned)
            box_sign = await self.client.crypto.signing_box_sign(
                params=sign_params)

            # Get signature by keys
            sign_params = ParamsOfSign(unsigned=unsigned, keys=keys)
            keys_sign = await self.client.crypto.sign(params=sign_params)

            self.assertEqual(keys_sign.signature, box_sign.signature)

            await self.client.crypto.remove_signing_box(params=external_box)

        asyncio.run(__main())

    def test_register_signing_box_app_object(self):  # Crypto
        class TestAppSigningBox(AppSigningBox):
            """
            AppSigningBox implementation class.
            Here we passed `box_handle` as init argument only for testing
            purposes, in real world it should use its own keys
            """

            def __init__(self, client, box_handle):
                super(TestAppSigningBox, self).__init__(client=client)
                self.box_handle = box_handle

            async def perform_get_public_key(self) -> str:
                result = await self.client.crypto.signing_box_get_public_key(
                    params=self.box_handle)
                return result.pubkey

            async def perform_sign(
                    self, params: ParamsOfAppSigningBox.Sign) -> str:
                params = ParamsOfSigningBoxSign(
                    signing_box=self.box_handle.handle,
                    unsigned=params.unsigned)
                result = await self.client.crypto.signing_box_sign(
                    params=params)

                return result.signature

        async def __main():
            keys = await self.client.crypto.generate_random_sign_keys()
            keys_box_handle = await self.client.crypto.get_signing_box(
                params=keys)

            app_signin_box = TestAppSigningBox(
                client=self.client, box_handle=keys_box_handle)

            # Get external signing box
            external_box = await self.client.crypto.register_signing_box(
                callback=app_signin_box.dispatcher)

            # Request box public key
            box_pubkey = await self.client.crypto.signing_box_get_public_key(
                params=external_box)
            self.assertEqual(keys.public, box_pubkey.pubkey)

            # Get signature from signing box
            unsigned = base64.b64encode(b'Test Message').decode()
            sign_params = ParamsOfSigningBoxSign(
                signing_box=external_box.handle, unsigned=unsigned)
            box_sign = await self.client.crypto.signing_box_sign(
                params=sign_params)

            # Get signature by keys
            sign_params = ParamsOfSign(unsigned=unsigned, keys=keys)
            keys_sign = await self.client.crypto.sign(params=sign_params)

            self.assertEqual(keys_sign.signature, box_sign.signature)

            await self.client.crypto.remove_signing_box(params=external_box)
        asyncio.run(__main())

    def test_parse_message(self):  # Boc
        async def __main():
            message = 'te6ccgEBAQEAWAAAq2n+AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAE/zMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzMzSsG8DgAAAAAjuOu9NAL7BxYpA'
            params = ParamsOfParse(boc=message)
            result = await self.client.boc.parse_message(params=params)
            self.assertEqual(
                'dfd47194f3058ee058bfbfad3ea40cbbd9ad17ca77cd0904d4d9f18a48c2fbca',
                result.parsed['id'])
            self.assertEqual(
                '-1:0000000000000000000000000000000000000000000000000000000000000000',
                result.parsed['src'])
            self.assertEqual(
                '-1:3333333333333333333333333333333333333333333333333333333333333333',
                result.parsed['dst'])

            with self.assertRaises(TonException):
                params = ParamsOfParse(boc='Wrong==')
                await self.client.boc.parse_message(params=params)

        asyncio.run(__main())

    def test_subscribe_collection(self):  # Net
        async def __main():
            results = []

            def __callback(response_data, response_type, *args):
                if response_type == SubscriptionResponseType.OK:
                    result = ResultOfSubscription(**response_data)
                    results.append(result.result)
                if response_type == SubscriptionResponseType.ERROR:
                    raise TonException(error=ClientError(**response_data))

            now = int(datetime.now().timestamp())
            q_params = ParamsOfSubscribeCollection(
                collection='messages', result='created_at',
                filter={'created_at': {'gt': now}})
            subscription = await self.client.net.subscribe_collection(
                params=q_params, callback=__callback)

            while True:
                if len(results) > 0 or \
                        int(datetime.now().timestamp()) > now + 10:
                    await self.client.net.unsubscribe(params=subscription)
                    break
                await asyncio.sleep(1)

            self.assertGreater(len(results), 0)

        asyncio.run(__main())

    def test_run_executor_acc_none(self):  # Tvm
        async def __main():
            message = 'te6ccgEBAQEAXAAAs0gAV2lB0HI8/VEO/pBKDJJJeoOcIh+dL9JzpmRzM8PfdicAPGNEGwRWGaJsR6UYmnsFVC2llSo1ZZN5mgUnCiHf7ZaUBKgXyAAGFFhgAAAB69+UmQS/LjmiQA=='
            run_params = ParamsOfRunExecutor(
                message=message, account=AccountForExecutor.NoAccount(),
                skip_transaction_check=True, return_updated_account=True)
            result = await self.client.tvm.run_executor(params=run_params)

            parse_params = ParamsOfParse(boc=result.account)
            parsed = await self.client.boc.parse_account(params=parse_params)
            self.assertEqual(
                '0:f18d106c11586689b11e946269ec1550b69654a8d5964de668149c28877fb65a',
                parsed.parsed['id'])
            self.assertEqual('Uninit', parsed.parsed['acc_type_name'])

        asyncio.run(__main())

    def test_convert_address(self):  # Utils
        async def __main():
            account_id = 'fcb91a3a3816d0f7b8c2c76108b8a9bc5a6b7a55bd79f8ab101c52db29232260'
            hex_ = '-1:fcb91a3a3816d0f7b8c2c76108b8a9bc5a6b7a55bd79f8ab101c52db29232260'
            hex_workchain0 = '0:fcb91a3a3816d0f7b8c2c76108b8a9bc5a6b7a55bd79f8ab101c52db29232260'
            base64 = 'Uf/8uRo6OBbQ97jCx2EIuKm8Wmt6Vb15+KsQHFLbKSMiYG+9'
            base64url = 'kf_8uRo6OBbQ97jCx2EIuKm8Wmt6Vb15-KsQHFLbKSMiYIny'

            convert_params = ParamsOfConvertAddress(
                address=account_id, output_format=AddressStringFormat.Hex())
            converted = await self.client.utils.convert_address(
                params=convert_params)
            self.assertEqual(hex_workchain0, converted.address)

            convert_params = ParamsOfConvertAddress(
                address=converted.address,
                output_format=AddressStringFormat.AccountId())
            converted = await self.client.utils.convert_address(
                params=convert_params)
            self.assertEqual(account_id, converted.address)

            convert_params = ParamsOfConvertAddress(
                address=hex_,
                output_format=AddressStringFormat.Base64(
                    url=False, test=False, bounce=False))
            converted = await self.client.utils.convert_address(
                params=convert_params)
            self.assertEqual(base64, converted.address)

            convert_params = ParamsOfConvertAddress(
                address=base64,
                output_format=AddressStringFormat.Base64(
                    url=True, test=True, bounce=True))
            converted = await self.client.utils.convert_address(
                params=convert_params)
            self.assertEqual(base64url, converted.address)

            convert_params = ParamsOfConvertAddress(
                address=base64url,
                output_format=AddressStringFormat.Hex())
            converted = await self.client.utils.convert_address(
                params=convert_params)
            self.assertEqual(hex_, converted.address)

            with self.assertRaises(TonException):
                convert_params = ParamsOfConvertAddress(
                    address='-1:00',
                    output_format=AddressStringFormat.Hex())
                await self.client.utils.convert_address(params=convert_params)

        asyncio.run(__main())

    def test_encryption_box_app_object(self):
        class TestAppEncryptionBox(AppEncryptionBox):
            async def perform_get_info(self) -> EncryptionBoxInfo:
                return EncryptionBoxInfo(algorithm='duplicator')

            async def perform_encrypt(
                    self, params: ParamsOfAppEncryptionBox.Encrypt) -> str:
                return params.data * 2

            async def perform_decrypt(
                    self, params: ParamsOfAppEncryptionBox.Decrypt) -> str:
                end = int(len(params.data) / 2)
                return params.data[:end]

        async def __main():
            # Register box
            app_encryption_box = TestAppEncryptionBox(client=self.client)
            box = await self.client.crypto.register_encryption_box(
                callback=app_encryption_box.dispatcher)

            # Get info
            info_result = await self.client.crypto.encryption_box_get_info(
                params=ParamsOfEncryptionBoxGetInfo(encryption_box=box.handle))
            self.assertEqual(info_result.info.algorithm, 'duplicator')

            # Encrypt
            enc_data = '12345'
            params = ParamsOfEncryptionBoxEncrypt(
                encryption_box=box.handle, data=enc_data)
            enc_result = await self.client.crypto.encryption_box_encrypt(
                params=params)
            self.assertEqual(enc_data * 2, enc_result.data)

            # Decrypt
            params = ParamsOfEncryptionBoxDecrypt(
                encryption_box=box.handle, data=enc_result.data)
            dec_result = await self.client.crypto.encryption_box_decrypt(
                params=params)
            self.assertEqual(enc_data, dec_result.data)

            # Remove box
            await self.client.crypto.remove_encryption_box(params=box)
        asyncio.run(__main())
