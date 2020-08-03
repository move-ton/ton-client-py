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


if __name__ == '__main__':
    unittest.main()
