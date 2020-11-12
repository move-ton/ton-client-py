import unittest

from tonclient.bindings.lib import LIB_VERSION
from tonclient.client import TonClient, DEVNET_BASE_URL


class TestTonClientAsyncCore(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TonClient(network={'server_address': DEVNET_BASE_URL})

    def test_version(self):
        self.assertEqual(LIB_VERSION, self.client.version())

    def test_get_api_reference(self):
        reference = self.client.get_api_reference()
        self.assertGreater(len(reference['modules']), 0)

    def test_build_info(self):
        info = self.client.build_info()
        self.assertNotEqual(None, info.get('build_number'))

    def test_destroy_context(self):
        self.client.destroy_context()


class TestTonClientSyncCore(unittest.TestCase):
    """ Sync core is not recommended to use """
    def setUp(self) -> None:
        self.client = TonClient(
            network={'server_address': DEVNET_BASE_URL}, is_core_async=False)

    def test_version(self):
        self.assertEqual(LIB_VERSION, self.client.version())

    def test_get_api_reference(self):
        reference = self.client.get_api_reference()
        self.assertGreater(len(reference['modules']), 0)

    def test_build_info(self):
        info = self.client.build_info()
        self.assertNotEqual(None, info.get('build_number'))

    def test_destroy_context(self):
        self.client.destroy_context()
