import os
import unittest

from tonsdk.lib import TonClient, DEVNET_BASE_URL
from tonsdk.contracts.contracts import TonContract


SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "samples")
CLIENT = TonClient(servers=[DEVNET_BASE_URL])
CONTRACT = TonContract()
CONTRACT.set_client(client=CLIENT)


class TestContractBase(unittest.TestCase):
    def setUp(self):
        self.valid_keypair = {
            "public": "c078fbff6a4daed8ab8d78d2371a99778c4a3a058fd4e4079e093e5a19b44722",
            "secret": "6fc0531fd1d0a76704cc0e2e1f1e827abb953aa03be39b5fdbebf6dcbfdba14b"
        }
        self.valid_image = "te6ccgEBEAEA7wACATQDAQEBwAIAU6AAAAAAAAehIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAIo/wAgwAH0pCBYkvSg4YrtU1gw9KAGBAEK9KQg9KEFABqgAAAAAXDtR2+NMO1XAgEgCAcAHv/wAiHwA/AF0x8B8AHwAQIC3AsJAgFIDQoASxwgggPQkCmCO1E0PQFgED0DPLgZPQFgED0FMj0AMntRwFvjO1XgAgEgDwwCASAODQADNCAAPQgxwLyaNUgxwCRMOAh+QEBgQIA1xjT/zD5EPKo2zCAAI0IfAE8AUyIMcB3NMfAfAB8AGA=="
        self.contract = TonContract()

    def test_load_keypair(self):
        # Load from binary file
        self.contract.load_keypair(
            path=os.path.join(SAMPLES_DIR, 'keys_binary.json'), binary=True)
        self.assertEqual(self.contract.keypair, self.valid_keypair)

        # Load from json file
        self.contract.load_keypair(
            path=os.path.join(SAMPLES_DIR, 'keys_raw.json'), binary=False)
        self.assertEqual(self.contract.keypair, self.valid_keypair)

    def test_load_image(self):
        self.contract.load_image(
            path=os.path.join(SAMPLES_DIR, 'PiggyBank', 'PiggyBank.tvc'))
        self.assertEqual(self.contract.image_b64, self.valid_image)


class TestSimpleWalletContract(unittest.TestCase):
    """
    Simple wallet contract tests
    """
    abi_path = os.path.join(SAMPLES_DIR, 'SimpleWallet', 'Wallet.abi.json')
    image_path = os.path.join(SAMPLES_DIR, 'SimpleWallet', 'Wallet.tvc')
    keypair_path = os.path.join(SAMPLES_DIR, 'keys_raw.json')

    def setUp(self):
        # Setup contract
        self.contract = CONTRACT
        self.contract.load_abi(path=self.abi_path)
        self.contract.load_image(path=self.image_path)
        self.contract.load_keypair(path=self.keypair_path, binary=False)

        self.contract_address = "0:2df86dd43c3fcd8cd9704126a6ecb6439116b39f0f9fb97c239dd67bdb6896b8"
        self.constructor_params = {}
        self.init_params = {}

    def test_deploy_message(self):
        result = self.contract.deploy_message(
            constructor_params=self.constructor_params,
            init_params=self.init_params)

        self.assertEqual(result["address"], self.contract_address)
        self.assertEqual(self.contract.address, self.contract_address)

    def test_deploy(self):
        result = self.contract.deploy(
            constructor_params=self.constructor_params,
            init_params=self.init_params
        )

        self.assertEqual(result["address"], self.contract_address)
        self.assertEqual(self.contract.address, self.contract_address)


class TestPiggyBankContract(unittest.TestCase):
    """
    Piggy bank contract tests
    """
    abi_path = os.path.join(SAMPLES_DIR, 'PiggyBank', 'PiggyBank.abi.json')
    image_path = os.path.join(SAMPLES_DIR, 'PiggyBank', 'PiggyBank.tvc')
    keypair_path = os.path.join(SAMPLES_DIR, 'keys_raw.json')

    def setUp(self):
        # Setup contract
        self.contract = CONTRACT
        self.contract.load_abi(path=self.abi_path)
        self.contract.load_image(path=self.image_path)
        self.contract.load_keypair(path=self.keypair_path, binary=False)

        self.owner_address = "0:1ab22c364214e24b782bc4966e23874b1c0cc682e8dba2d24a0561bb27d04221"
        self.contract_address = "0:668b5c83056ebf1852cc7af4e61c8a421056c0311f035a39e5baf7ce28b14728"
        self.constructor_params = {
            "pb_owner": self.owner_address,
            "pb_limit": 5 * 10**9
        }
        self.init_params = {}

    def test_deploy_message(self):
        result = self.contract.deploy_message(
            constructor_params=self.constructor_params,
            init_params=self.init_params)

        self.assertEqual(result["address"], self.contract_address)
        self.assertEqual(self.contract.address, self.contract_address)

    def test_deploy_message_unsigned(self):
        result = self.contract.deploy_message_unsigned(
            constructor_params=self.constructor_params,
            init_params=self.init_params)

        self.assertEqual(result["addressHex"], self.contract_address)

    def test_deploy(self):
        result = self.contract.deploy(
            constructor_params=self.constructor_params,
            init_params=self.init_params)

        self.assertEqual(result["address"], self.contract_address)
        self.assertEqual(self.contract.address, self.contract_address)

    def test_run_message(self):
        self.contract.address = self.contract_address
        result = self.contract.run_message(function_name="getVersion")

        self.assertEqual(result["address"], self.contract_address)
        self.assertEqual(
            list(result.keys()),
            ["address", "messageId", "messageBodyBase64", "expire"])

    def test_run_message_unsigned(self):
        self.contract.address = self.contract_address
        result = self.contract.run_message(function_name="getVersion")

        self.assertEqual(result["address"], self.contract_address)
        self.assertEqual(
            list(result.keys()),
            ["address", "messageId", "messageBodyBase64", "expire"])

    def test_run_body(self):
        result = self.contract.run_body(function_name="getVersion")
        self.assertEqual(
            "te6ccgEBAQEATwAA" in result["bodyBase64"], True)

        result = self.contract.run_body(
            function_name="getVersion", internal=True)
        self.assertEqual(result["bodyBase64"], "te6ccgEBAQEABgAACFoZzZI=")

    def test_run(self):
        self.contract.address = self.contract_address
        result = self.contract.run(function_name="getData")

        self.assertEqual(result["output"]["value0"], self.owner_address)

    def test_sign_message(self):
        # Create unsigned message
        self.contract.address = self.contract_address
        result = self.contract.run_message_unsigned(function_name="getVersion")

        # Sign message
        result = self.contract.sign_message(
            unsigned_base64=result["unsignedBytesBase64"],
            sign_base64=result["bytesToSignBase64"])

        self.assertEqual(result["address"], self.contract_address)
        self.assertEqual(
            "te6ccgEBAQEAUQAAnYgAzRa5BgrdfjClmPXpzDkUhCCtgGI" in result["messageBodyBase64"],
            True)


if __name__ == '__main__':
    unittest.main()
