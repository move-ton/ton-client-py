import json
import os
import unittest
import base64

from tonsdk.client import TonClient, DEVNET_BASE_URL
from tonsdk.errors import TonException
from tonsdk.types import KeyPair, FmtString, NACL_OUTPUT_B64

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "samples")
client = TonClient(servers=[DEVNET_BASE_URL])


class TestBase(unittest.TestCase):
    abi_path = None
    image_path = None
    keypair_path = None

    def setUp(self) -> None:
        with open(self.abi_path) as fp:
            self.abi = json.loads(fp.read())
        with open(self.image_path, "rb") as fp:
            self.image_b64 = base64.b64encode(fp.read()).decode()
        self.keypair = KeyPair.load(path=self.keypair_path, is_binary=False)


class TestSimpleWalletContract(TestBase):
    """
    Simple wallet contract tests
    """
    abi_path = os.path.join(SAMPLES_DIR, 'SimpleWallet', 'Wallet.abi.json')
    image_path = os.path.join(SAMPLES_DIR, 'SimpleWallet', 'Wallet.tvc')
    keypair_path = os.path.join(SAMPLES_DIR, 'keys_raw.json')

    def setUp(self):
        super(TestSimpleWalletContract, self).setUp()
        self.contract_address = "0:2df86dd43c3fcd8cd9704126a6ecb6439116b39f0f9fb97c239dd67bdb6896b8"

    def test_load(self):
        result = client.contracts.load(address=self.contract_address)
        self.assertEqual(result["id"], self.contract_address[2:])
        self.assertEqual(result["balanceGrams"].isnumeric(), True)

    def test_deploy_address(self):
        address = client.contracts.deploy_address(
            abi=self.abi, image_b64=self.image_b64, keypair=self.keypair)
        self.assertEqual(address, self.contract_address)

    def test_address_convert(self):
        address = client.contracts.address_convert(
            address=self.contract_address, to="Base64",
            b64_params={"url": False, "test": True, "bounce": True})
        self.assertEqual(address, "kQAt+G3UPD/NjNlwQSam7LZDkRaznw+fuXwjndZ722iWuK11")

        def __callable_to():
            client.contracts.address_convert(
                address=self.contract_address, to="Base")
        self.assertRaises(TonException, __callable_to)

        def __callable_b64():
            client.contracts.address_convert(
                address=self.contract_address, to="Base64",
                b64_params={"url": False, "test": True})
        self.assertRaises(TonException, __callable_b64)

    def test_deploy_message(self):
        message = client.contracts.deploy_message(
            abi=self.abi, image_b64=self.image_b64, keypair=self.keypair)
        self.assertEqual(message["address"], self.contract_address)

    def test_deploy_encode_unsigned_message(self):
        message, address = client.contracts.deploy_encode_unsigned_message(
            abi=self.abi, image_b64=self.image_b64, public=self.keypair.public)
        self.assertIsNotNone(message["unsignedBytesBase64"])
        self.assertIsNotNone(message["bytesToSignBase64"])
        self.assertEqual(address, self.contract_address)

    def test_deploy_data(self):
        result = client.contracts.deploy_data(
            abi=self.abi, image_b64=self.image_b64, public=self.keypair.public)
        self.assertEqual(result["dataBase64"], "te6ccgEBAgEAKAABAcABAEPQMB4+/9qTa7Yq4140jcamXeMSjoFj9TkB54JPloZtEcig")

        result = client.contracts.deploy_data(public=self.keypair.public)
        self.assertEqual(result["dataBase64"], "te6ccgEBAgEAKAABAcABAEPQMB4+/9qTa7Yq4140jcamXeMSjoFj9TkB54JPloZtEcig")

    def test_deploy(self):
        result = client.contracts.deploy(
            abi=self.abi, image_b64=self.image_b64, keypair=self.keypair)
        self.assertEqual(result["address"], self.contract_address)


class TestPiggyBankContract(TestBase):
    """
    Piggy bank contract tests
    """
    abi_path = os.path.join(SAMPLES_DIR, 'PiggyBank', 'PiggyBank.abi.json')
    image_path = os.path.join(SAMPLES_DIR, 'PiggyBank', 'PiggyBank.tvc')
    keypair_path = os.path.join(SAMPLES_DIR, 'keys_raw.json')

    def setUp(self):
        super(TestPiggyBankContract, self).setUp()

        self.contract_address = "0:668b5c83056ebf1852cc7af4e61c8a421056c0311f035a39e5baf7ce28b14728"
        self.owner_address = "0:1ab22c364214e24b782bc4966e23874b1c0cc682e8dba2d24a0561bb27d04221"
        self.constructor_params = {
            "pb_owner": self.owner_address,
            "pb_limit": 5 * 10 ** 9
        }

    def test_run_message(self):
        message = client.contracts.run_message(
            abi=self.abi, address=self.contract_address, keypair=self.keypair,
            function_name="getVersion")
        self.assertEqual(message["address"], self.contract_address)

        message = client.contracts.run_message(
            address=self.contract_address, abi=self.abi,
            function_name="getVersion")
        self.assertEqual(message["address"], self.contract_address)

    def test_run_encode_unsigned_message(self):
        message = client.contracts.run_encode_unsigned_message(
            abi=self.abi, address=self.contract_address,
            function_name="getVersion")
        self.assertIsNotNone(message["unsignedBytesBase64"])
        self.assertIsNotNone(message["bytesToSignBase64"])

    def test_run_body(self):
        body = client.contracts.run_body(
            abi=self.abi, keypair=self.keypair, function_name="getVersion")
        self.assertEqual("te6ccgEBAQEATwAA" in body, True)

        body = client.contracts.run_body(
            abi=self.abi, keypair=self.keypair, function_name="getVersion",
            internal=True)
        self.assertEqual(body, "te6ccgEBAQEABgAACFoZzZI=")

        body = client.contracts.run_body(
            abi=self.abi, function_name="getVersion")
        self.assertIsNotNone(body)

    def test_run(self):
        result = client.contracts.run(
            abi=self.abi, address=self.contract_address, keypair=self.keypair,
            function_name="getData")
        self.assertEqual(result["output"]["value0"], self.owner_address)

        result = client.contracts.run(
            address=self.contract_address, abi=self.abi,
            function_name="getVersion")
        self.assertEqual(result["output"]["value0"], "0x1")

    def test_run_local_message(self):
        message = client.contracts.run_message(
            address=self.contract_address, abi=self.abi,
            function_name="getVersion")

        result = client.contracts.run_local_message(
            address=self.contract_address, function_name="getVersion",
            message_b64=message["messageBodyBase64"], abi=self.abi)
        self.assertEqual(result["output"]["value0"], "0x1")
        self.assertIsNone(result["fees"])

        result = client.contracts.run_local_message(
            address=self.contract_address,
            message_b64=message["messageBodyBase64"], full_run=True)
        self.assertIsNotNone(result["fees"])

    def test_run_local(self):
        result = client.contracts.run_local(
            address=self.contract_address, abi=self.abi,
            function_name="getVersion")
        self.assertIsNone(result["fees"])

        result = client.contracts.run_local(
            address=self.contract_address, abi=self.abi,
            function_name="getVersion", full_run=True)
        self.assertIsNotNone(result["fees"])

    def test_run_output(self):
        # Body base64 of 'getVersion' out message
        body = "te6ccgEBAQEAJgAASNoZzZIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQ=="
        output = client.contracts.run_output(
            abi=self.abi, function_name="getVersion", body_b64=body)
        self.assertEqual(output["value0"], "0x1")

    def test_run_fee(self):
        result = client.contracts.run_fee(
            address=self.contract_address, abi=self.abi,
            function_name="getVersion")
        self.assertEqual(result["output"]["value0"], "0x1")

    def test_run_fee_message(self):
        message = client.contracts.run_message(
            address=self.contract_address, abi=self.abi,
            function_name="getVersion")

        result = client.contracts.run_fee_message(
            address=self.contract_address,
            message_b64=message["messageBodyBase64"])
        self.assertIsNotNone(result["fees"])

    def test_run_unknown_input(self):
        body = client.contracts.run_body(
            abi=self.abi, function_name="getVersion")
        unknown = client.contracts.run_unknown_input(
            abi=self.abi, body_b64=body)
        self.assertEqual(unknown, {"function": "getVersion", "output": {}})

    def test_run_unknown_output(self):
        # Body base64 for 'getVersion' out message
        body = "te6ccgEBAQEAJgAASNoZzZIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQ=="
        unknown = client.contracts.run_unknown_output(
            abi=self.abi, body_b64=body)
        self.assertEqual(unknown, {"function": "getVersion", "output": {"value0": "0x1"}})

    def test_encode_message_with_sign(self):
        # Create unsigned message
        unsigned = client.contracts.run_encode_unsigned_message(
            address=self.contract_address, abi=self.abi,
            function_name="getVersion")

        # Create signature
        signature = client.crypto.nacl_sign_detached(
            secret=f"{self.keypair.secret}{self.keypair.public}",
            message_fmt=FmtString(unsigned["bytesToSignBase64"]).base64,
            output_fmt=NACL_OUTPUT_B64)
        unsigned["signBytesBase64"] = signature

        # Sign message
        signed = client.contracts.encode_message_with_sign(
            abi=self.abi, message=unsigned)
        self.assertEqual(signed["address"], self.contract_address)

        # Run message
        result = client.contracts.process_message(
            message=signed, abi=self.abi, function_name="getVersion")
        self.assertEqual(result["output"]["value0"], "0x1")

    def test_parse_message(self):
        message_boc = "te6ccgEBAQEAcQAA3YgAzRa5BgrdfjClmPXpzDkUhCCtgGI+BrRzy3XvnFFijlAGkFJ1s8KnJdQgxR+kLP+yGcqn44lVZeU8uxDkYRvny3R/yxeAzUDFMudyk6jKu2fqeazMGmcUKztS4MSgNFscKAAABc8AC9m5TL3Gng=="
        result = client.contracts.parse_message(boc_b64=message_boc)
        self.assertDictEqual(result, {"dst": "0:668b5c83056ebf1852cc7af4e61c8a421056c0311f035a39e5baf7ce28b14728"})

    def test_function_id(self):
        fn_id = client.contracts.function_id(
            abi=self.abi, function_name="getVersion")
        self.assertEqual(fn_id, 1511640466)

    def test_find_shard(self):
        shards = [
            {"workchain_id": 0, "shard": "0800000000000000"},
            {"workchain_id": 0, "shard": "1800000000000000"}
        ]
        result = client.contracts.find_shard(
            address=self.contract_address, shards=shards)
        self.assertIsNone(result)

    def test_send_message(self):
        message = client.contracts.run_message(
            address=self.contract_address, abi=self.abi,
            function_name="getVersion")
        result = client.contracts.send_message(message=message)
        self.assertIsNotNone(result.values())

    def test_process_message(self):
        message = client.contracts.run_message(
            address=self.contract_address, abi=self.abi,
            function_name="getVersion")

        result_unknown = client.contracts.process_message(message=message)
        self.assertIsNone(result_unknown["output"])

        output = client.contracts.run_unknown_output(
            abi=self.abi,
            body_b64=result_unknown["transaction"]["out_messages"][0]["body"])
        self.assertEqual(output["output"]["value0"], "0x1")

    def test_process_transaction(self):
        # TODO: Write test
        result = client.contracts.run(
            address=self.contract_address, abi=self.abi,
            function_name="getVersion")
        processed = client.contracts.process_transaction(
            address=self.contract_address, transaction=result["transaction"])

    def test_wait_transaction(self):
        message = client.contracts.run_message(
            address=self.contract_address, abi=self.abi,
            function_name="getVersion")
        state = client.contracts.send_message(message=message)

        unknown_output = client.contracts.wait_transaction(
            message=message, state=state)
        self.assertIsNone(unknown_output["output"])

    def test_tvm_get(self):
        # TODO: Write test
        pass

    def test_resolve_error(self):
        # TODO: Write test
        pass


if __name__ == '__main__':
    unittest.main()
