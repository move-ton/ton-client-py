import aiounittest

from tonclient.bindings.lib import LIB_VERSION
from tonclient.client import TonClient, DEVNET_BASE_URL


class TestTonClientAsync(aiounittest.AsyncTestCase):
    def setUp(self) -> None:
        self.client = TonClient(
            network={'server_address': DEVNET_BASE_URL}, is_async=True)

    async def test_version(self):
        version = await self.client.version()
        self.assertEqual(LIB_VERSION, version)

    async def test_get_api_reference(self):
        reference = await self.client.get_api_reference()
        self.assertEqual(LIB_VERSION, reference['version'])

    def test_destroy_context(self):
        self.client.destroy_context()
