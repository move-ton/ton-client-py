import unittest

from tonclient.client import TonClient, DEVNET_BASE_URL

client = TonClient(network={'server_address': DEVNET_BASE_URL})


class TestTonProcessing(unittest.TestCase):
    def test_process_message(self):
        client.processing.process_message()
