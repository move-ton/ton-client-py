"""Everscale client module"""
from typing import Awaitable, Union

from tonclient.bindings.lib import (
    tc_create_context,
    tc_destroy_context,
    tc_read_string,
    tc_destroy_string,
)
from tonclient.bindings.types import TCClientContext, TCSyncResponseData
from tonclient.boc import TonBoc
from tonclient.debot import TonDebot
from tonclient.errors import TonException
from tonclient.module import TonModule
from tonclient.crypto import TonCrypto
from tonclient.net import TonNet
from tonclient.abi import TonAbi
from tonclient.processing import TonProcessing
from tonclient.proofs import TonProofs
from tonclient.tvm import TonTvm
from tonclient.types import (
    ClientError,
    ClientConfig,
    ResultOfVersion,
    ResultOfGetApiReference,
    ResultOfBuildInfo,
    ParamsOfResolveAppRequest,
)
from tonclient.utils import TonUtils


DEVNET_BASE_URLS = [
    'eri01.net.everos.dev',
    'rbx01.net.everos.dev',
    'gra01.net.everos.dev',
]
MAINNET_BASE_URLS = [
    'eri01.main.everos.dev',
    'gra01.main.everos.dev',
    'gra02.main.everos.dev',
    'lim01.main.everos.dev',
    'rbx01.main.everos.dev',
]


class TonClientBase(TonModule):
    """Client module methods"""

    def version(self) -> Union[ResultOfVersion, Awaitable[ResultOfVersion]]:
        """Returns Core Library version"""
        response = self.request(method='client.version')
        return self.response(classname=ResultOfVersion, response=response)

    def get_api_reference(
        self,
    ) -> Union[ResultOfGetApiReference, Awaitable[ResultOfGetApiReference]]:
        """Returns Core Library API reference"""
        response = self.request(method='client.get_api_reference')
        return self.response(classname=ResultOfGetApiReference, response=response)

    def build_info(self) -> Union[ResultOfBuildInfo, Awaitable[ResultOfBuildInfo]]:
        """Get build info"""
        response = self.request(method='client.build_info')
        return self.response(classname=ResultOfBuildInfo, response=response)

    def resolve_app_request(
        self, params: ParamsOfResolveAppRequest
    ) -> Union[None, Awaitable[None]]:
        """Resolves application request processing result"""
        return self.request(method='client.resolve_app_request', **params.dict)

    def config(self) -> Union[ClientConfig, Awaitable[ClientConfig]]:
        """Get client config"""
        response = self.request(method='client.config')
        return self.response(classname=ClientConfig, response=response)


class TonClient:
    """Main client class to create object of"""

    def __init__(
        self, config: ClientConfig, is_core_async: bool = True, is_async: bool = False
    ):
        """
        :param config: ClientConfig object
        :param is_core_async: Use sync or async core requests
        :param is_async: Client mode
        """
        super().__init__()

        self._ctx = self.create_context(config=config)
        self._is_core_async = is_core_async
        self._is_async = is_async

        self.base = TonClientBase(client=self)
        self.crypto = TonCrypto(client=self)
        self.net = TonNet(client=self)
        self.abi = TonAbi(client=self)
        self.boc = TonBoc(client=self)
        self.processing = TonProcessing(client=self)
        self.utils = TonUtils(client=self)
        self.tvm = TonTvm(client=self)
        self.debot = TonDebot(client=self)
        self.proofs = TonProofs(client=self)

    @property
    def config(self):
        """Client config"""
        return self.base.config

    @property
    def ctx(self):
        """Client context"""
        return self._ctx

    @property
    def is_core_async(self):
        """Client core mode"""
        return self._is_core_async

    @property
    def is_async(self):
        """Client mode"""
        return self._is_async

    @property
    def version(self):
        """Client base shortcut"""
        return self.base.version

    @property
    def get_api_reference(self):
        """Client base shortcut"""
        return self.base.get_api_reference

    @property
    def build_info(self):
        """Client base shortcut"""
        return self.base.build_info

    @property
    def resolve_app_request(self):
        """Client base shortcut"""
        return self.base.resolve_app_request

    @staticmethod
    def create_context(config: ClientConfig) -> TCClientContext:
        """Create context"""
        response_ptr = tc_create_context(config=config.dict)
        response = TCSyncResponseData(tc_read_string(string=response_ptr))
        is_success, result, error = (
            response.is_success,
            response.result,
            response.error,
        )
        tc_destroy_string(response_ptr)

        if not is_success:
            raise TonException(error=ClientError(**error))

        return TCClientContext(result)

    def destroy_context(self):
        """Destroy context"""
        tc_destroy_context(ctx=self._ctx)
