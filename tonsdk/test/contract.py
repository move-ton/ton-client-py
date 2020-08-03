import os
import unittest

from tonsdk.lib import TonClient, DEVNET_BASE_URL
from tonsdk.contracts.contracts import TonContract


SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "samples")
CLIENT = TonClient()
CLIENT.setup(settings={"baseUrl": DEVNET_BASE_URL})


class ContractBaseTest(unittest.TestCase):
    def setUp(self) -> None:
        self.valid_keypair_binary = {
            'public': 'c078fbff6a4daed8ab8d78d2371a99778c4a3a058fd4e4079e093e5a19b44722',
            'secret': '6fc0531fd1d0a76704cc0e2e1f1e827abb953aa03be39b5fdbebf6dcbfdba14b'
        }
        self.valid_keypair_raw = {
            "public": "37a2c179b676a2e386d6efe0c7199e376afe2f35d1a62e826c1a25b0bd2ef24e",
            "secret": "5cfdb695023413591deade0d0889ef344a317f3c178c5d6d690764ef62aa93f1"
        }
        self.valid_image = "te6ccgEBEAEA7wACATQDAQEBwAIAU6AAAAAAAAehIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAIo/wAgwAH0pCBYkvSg4YrtU1gw9KAGBAEK9KQg9KEFABqgAAAAAXDtR2+NMO1XAgEgCAcAHv/wAiHwA/AF0x8B8AHwAQIC3AsJAgFIDQoASxwgggPQkCmCO1E0PQFgED0DPLgZPQFgED0FMj0AMntRwFvjO1XgAgEgDwwCASAODQADNCAAPQgxwLyaNUgxwCRMOAh+QEBgQIA1xjT/zD5EPKo2zCAAI0IfAE8AUyIMcB3NMfAfAB8AGA=="
        self.contract = TonContract()

    def test_load_keypair(self):
        # Load from binary file
        self.contract.load_keypair(
            path=os.path.join(SAMPLES_DIR, 'keys_binary.json'), binary=True)
        self.assertEqual(self.contract.keypair, self.valid_keypair_binary)

        # Load from json file
        self.contract.load_keypair(
            path=os.path.join(SAMPLES_DIR, 'keys.json'), binary=False)
        self.assertEqual(self.contract.keypair, self.valid_keypair_raw)

    def test_load_image(self):
        self.contract.load_image(
            path=os.path.join(SAMPLES_DIR, 'PiggyBank', 'PiggyBank.tvc'))
        self.assertEqual(self.contract.image_b64, self.valid_image)


class PiggyBankTest(unittest.TestCase):
    """
    Piggy bank contract tests
    """
    abi_path = os.path.join(SAMPLES_DIR, 'PiggyBank', 'PiggyBank.abi.json')
    image_path = os.path.join(SAMPLES_DIR, 'PiggyBank', 'PiggyBank.tvc')
    keypair_path = os.path.join(SAMPLES_DIR, 'keys.json')

    def setUp(self) -> None:
        # Setup contract
        contract = TonContract()
        contract.set_client(client=CLIENT)
        contract.load_abi(path=self.abi_path)
        contract.load_image(path=self.image_path)
        contract.load_keypair(path=self.keypair_path, binary=False)
        self.contract = contract

        self.owner_address = "0:1ab22c364214e24b782bc4966e23874b1c0cc682e8dba2d24a0561bb27d04221"
        self.contract_address = "0:07761d2935f08e2002da561ebfb89501ac6a2a904d2a92a083b694af5d103dc2"
        self.constructor_params = {
            "pb_owner": self.owner_address,
            "pb_limit": 5 * 10**9
        }
        self.init_params = {
            "owner": self.owner_address,
            "limit": 5 * 10**9,
            "balance": 0,
            "version": 1
        }

    def test_deploy_message(self):
        result = self.contract.deploy_message(
            constructor_params=self.constructor_params,
            init_params=self.init_params)

        self.assertEqual(result["address"], self.contract_address)
        self.assertEqual(self.contract.address, self.contract_address)

    def test_deploy(self):
        result = self.contract.deploy(
            constructor_params=self.constructor_params,
            init_params=self.init_params)
        print(result)


if __name__ == '__main__':
    unittest.main()
