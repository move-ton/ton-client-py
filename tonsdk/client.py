import asyncio
from typing import Dict

from tonsdk.bindings.lib import tc_create_context, tc_destroy_context
from tonsdk.crypto import TonCrypto
from tonsdk.module import TonRequestMixin
from tonsdk.queries import TonQuery

DEVNET_BASE_URL = 'net.ton.dev'
MAINNET_BASE_URL = 'main.ton.dev'

TON_CLIENT_DEFAULT_SETUP = {
    'servers': ['http://localhost'],
    'messageRetriesCount': 1,
    'messageExpirationTimeout': 50000,
    'messageExpirationTimeoutGrowFactor': 1.5,
    'messageProcessingTimeout': 50000,
    'messageProcessingTimeoutGrowFactor': 1.5,
    'waitForTimeout': 30000,
    'accessKey': ''
}


class TonClient(TonRequestMixin):
    """ Main client class to create object of """
    def __init__(self, **config):
        super(TonClient, self).__init__()
        self._ctx = tc_create_context()
        self.crypto = TonCrypto(ctx=self._ctx)
        self.queries = TonQuery(ctx=self._ctx)
        self.setup({**TON_CLIENT_DEFAULT_SETUP, **config})

    def setup(self, settings: Dict):
        self.request(method="setup", **settings)

    def version(self) -> str:
        return self.request(method="version")

    def destroy_context(self):
        tc_destroy_context(ctx=self._ctx)


async def main():
    t = TonClient(servers=[DEVNET_BASE_URL])
    print(await t.request_async('crypto.mnemonic.from.random', wordCount=12))


if __name__ == "__main__":
    asyncio.run(main())