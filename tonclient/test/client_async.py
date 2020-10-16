import unittest

from tonclient.bindings.lib import LIB_VERSION
from tonclient.client import TonClient, DEVNET_BASE_URL


class TestTonClientAsync(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TonClient(network={'server_address': DEVNET_BASE_URL})

    def test_version(self):
        version = self.client.version()
        self.assertEqual(LIB_VERSION, version)

    def test_get_api_reference(self):
        reference = self.client.get_api_reference()
        self.assertEqual(LIB_VERSION, reference['version'])

    def test_destroy_context(self):
        self.client.destroy_context()
