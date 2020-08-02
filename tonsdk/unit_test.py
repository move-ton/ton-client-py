import unittest

from tonsdk import lib


class TestTonClient(unittest.TestCase):

    def test_version(self):
        client = lib.TonClient()
        self.assertEqual(client.version()["result"], lib.LIB_VERSION)

    def test_crypto_func(self):
        client = lib.TonClient()
        mnemo = "machine logic master small before pole ramp ankle stage trash pepper success oxygen unhappy engine muscle party oblige situate cement fame keep inform lemon"
        self.assertEqual({"public": "2e750ea795aad6e04ae1544132619c6a5e1356c36db60532320dae6aa656cf2e", "secret": "7ee962326304f9f88d5048fabdde7921411b1aad6400ef984c85a0a9cb3b1a7c"}, client.request('crypto.mnemonic.derive.sign.keys', dict(phrase=mnemo))["result"])


class TestTonContracts(unittest.TestCase):
    def setUp(self) -> None:
        self.abi = {
            "ABI version": 2,
            "header": ["pubkey", "time", "expire"],
            "functions": [
                {
                    "name": "constructor",
                    "inputs": [
                        {"name": "owners", "type": "uint256[]"},
                        {"name": "reqConfirms", "type": "uint8"}
                    ],
                    "outputs": [
                    ]
                },
                {
                    "name": "acceptTransfer",
                    "inputs": [
                        {"name": "payload", "type": "bytes"}
                    ],
                    "outputs": [
                    ]
                },
                {
                    "name": "sendTransaction",
                    "inputs": [
                        {"name": "dest", "type": "address"},
                        {"name": "value", "type": "uint128"},
                        {"name": "bounce", "type": "bool"},
                        {"name": "flags", "type": "uint8"},
                        {"name": "payload", "type": "cell"}
                    ],
                    "outputs": [
                    ]
                },
                {
                    "name": "submitTransaction",
                    "inputs": [
                        {"name": "dest", "type": "address"},
                        {"name": "value", "type": "uint128"},
                        {"name": "bounce", "type": "bool"},
                        {"name": "allBalance", "type": "bool"},
                        {"name": "payload", "type": "cell"}
                    ],
                    "outputs": [
                        {"name": "transId", "type": "uint64"}
                    ]
                },
                {
                    "name": "confirmTransaction",
                    "inputs": [
                        {"name": "transactionId", "type": "uint64"}
                    ],
                    "outputs": [
                    ]
                },
                {
                    "name": "isConfirmed",
                    "inputs": [
                        {"name": "mask", "type": "uint32"},
                        {"name": "index", "type": "uint8"}
                    ],
                    "outputs": [
                        {"name": "confirmed", "type": "bool"}
                    ]
                },
                {
                    "name": "getParameters",
                    "inputs": [
                    ],
                    "outputs": [
                        {"name": "maxQueuedTransactions", "type": "uint8"},
                        {"name": "maxCustodianCount", "type": "uint8"},
                        {"name": "expirationTime", "type": "uint64"},
                        {"name": "minValue", "type": "uint128"},
                        {"name": "requiredTxnConfirms", "type": "uint8"}
                    ]
                },
                {
                    "name": "getTransaction",
                    "inputs": [
                        {"name": "transactionId", "type": "uint64"}
                    ],
                    "outputs": [
                        {"components": [{"name": "id", "type": "uint64"},
                                        {"name": "confirmationsMask",
                                         "type": "uint32"},
                                        {"name": "signsRequired",
                                         "type": "uint8"},
                                        {"name": "signsReceived",
                                         "type": "uint8"},
                                        {"name": "creator", "type": "uint256"},
                                        {"name": "index", "type": "uint8"},
                                        {"name": "dest", "type": "address"},
                                        {"name": "value", "type": "uint128"},
                                        {"name": "sendFlags",
                                         "type": "uint16"},
                                        {"name": "payload", "type": "cell"},
                                        {"name": "bounce", "type": "bool"}],
                         "name": "trans", "type": "tuple"}
                    ]
                },
                {
                    "name": "getTransactions",
                    "inputs": [
                    ],
                    "outputs": [
                        {"components": [{"name": "id", "type": "uint64"},
                                        {"name": "confirmationsMask",
                                         "type": "uint32"},
                                        {"name": "signsRequired",
                                         "type": "uint8"},
                                        {"name": "signsReceived",
                                         "type": "uint8"},
                                        {"name": "creator", "type": "uint256"},
                                        {"name": "index", "type": "uint8"},
                                        {"name": "dest", "type": "address"},
                                        {"name": "value", "type": "uint128"},
                                        {"name": "sendFlags",
                                         "type": "uint16"},
                                        {"name": "payload", "type": "cell"},
                                        {"name": "bounce", "type": "bool"}],
                         "name": "transactions", "type": "tuple[]"}
                    ]
                },
                {
                    "name": "getTransactionIds",
                    "inputs": [
                    ],
                    "outputs": [
                        {"name": "ids", "type": "uint64[]"}
                    ]
                },
                {
                    "name": "getCustodians",
                    "inputs": [
                    ],
                    "outputs": [
                        {"components": [{"name": "index", "type": "uint8"},
                                        {"name": "pubkey", "type": "uint256"}],
                         "name": "custodians", "type": "tuple[]"}
                    ]
                }
            ],
            "data": [
            ],
            "events": [
                {
                    "name": "TransferAccepted",
                    "inputs": [
                        {"name": "payload", "type": "bytes"}
                    ],
                    "outputs": [
                    ]
                }
            ]
        }
        self.keys = {
            "public": "6dd0530118f884c775e38cb9f5bb31200707eb99e73a1e6e621d720604cc3084",
            "secret": "12906742ad01dbe40d6079a83acdcd9c7c33420eca77c26f72d23359f606cce5"
        }
        self.address = "-1:2ac9e24350f1940158e017602126b48407cbb59c9c840eb4fdf58692dc864ff6"
        self.client = lib.TonClient()
        self.client.setup()

    def test_run_local(self):
        result = self.client.contracts.run_local(
            address=self.address, abi=self.abi, function_name="getCustodians",
            inputs={})

        self.assertEqual(result["success"], True)
        self.assertEqual(
            result["result"]["output"]["custodians"][0],
            {'index': '0x0', 'pubkey': '0x6dd0530118f884c775e38cb9f5bb31200707eb99e73a1e6e621d720604cc3084'})

    def test_run_local_msg(self):
        # TODO: Write normal test
        result = self.client.contracts.run_local_msg(
            address=self.address,
            message_base64="te6ccgEBAQEAWwAAsUn+VZPEhqHjKAKxwC7AQk1pCA+Xazk5CB1p++sNJbkMn+0AJ12JVRybYJ1rTbJFDFLz3rTAyeMnFHz/vVSYzUs80LzRZaC8AAbLc7wAAAAgrvFBhL3/a1BA",
            full_run=True, abi=self.abi)

        print(result)

    def test_run(self):
        # TODO: Find normal contract to test functions
        result = self.client.contracts.run(
            address=self.address, abi=self.abi, function_name="getCustodians",
            inputs={})
        print(result)

        self.assertEqual(result['success'], True)


if __name__ == '__main__':
    unittest.main()
