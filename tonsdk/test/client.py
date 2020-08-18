import unittest

from tonsdk.bindings.lib import LIB_VERSION
from tonsdk.client import TonClient, DEVNET_BASE_URL


class TestTonClient(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TonClient(servers=[DEVNET_BASE_URL])

    def test_version(self):
        self.assertEqual(self.client.version(), LIB_VERSION)

    def test_destroy_context(self):
        self.client.destroy_context()


if __name__ == '__main__':
    unittest.main()
