from typing import Dict, Union

from tonclient.bindings.lib import tc_create_context, tc_destroy_context, \
    tc_read_string, tc_destroy_string
from tonclient.bindings.types import TCClientContext, TCSyncResponseData
from tonclient.boc import TonBoc
from tonclient.decorators import Response
from tonclient.errors import TonException
from tonclient.module import TonModule
from tonclient.crypto import TonCrypto
from tonclient.net import TonNet
from tonclient.abi import TonAbi
from tonclient.processing import TonProcessing
from tonclient.utils import TonUtils

DEVNET_BASE_URL = 'net.ton.dev'
MAINNET_BASE_URL = 'main.ton.dev'

CLIENT_DEFAULT_SETUP = {
    'network': {
        'server_address': 'http://localhost',
        'message_retries_count': 5,
        'message_processing_timeout': 40000,
        'wait_for_timeout': 40000,
        'out_of_sync_threshold': 15000,
        'access_key': ''
    },
    'crypto': {
        'fish_param': ''
    },
    'abi': {
        'message_expiration_timeout': 40000,
        'message_expiration_timeout_grow_factor': 1.5
    }
}


class TonClientBase(TonModule):
    @Response.version
    def version(self) -> str:
        return self.request(function_name='client.version')

    @Response.get_api_reference
    def get_api_reference(self) -> Dict:
        return self.request(function_name='client.get_api_reference')


class TonClient(object):
    """ Main client class to create object of """
    def __init__(
            self, network: Dict[str, Union[str, int]] = None,
            crypto: Dict[str, str] = None,
            abi: Dict[str, Union[int, float]] = None, is_async: bool = False):
        super(TonClient, self).__init__()

        self._ctx = self.create_context(config={
            'network': {**CLIENT_DEFAULT_SETUP['network'], **(network or {})},
            'crypto': {**CLIENT_DEFAULT_SETUP['crypto'], **(crypto or {})},
            'abi': {**CLIENT_DEFAULT_SETUP['abi'], **(abi or {})}
        })
        self._is_async = is_async

        self.base = TonClientBase(ctx=self._ctx, is_async=is_async)
        self.crypto = TonCrypto(ctx=self._ctx, is_async=is_async)
        self.net = TonNet(ctx=self._ctx, is_async=is_async)
        self.abi = TonAbi(ctx=self._ctx, is_async=is_async)
        self.boc = TonBoc(ctx=self._ctx, is_async=is_async)
        self.processing = TonProcessing(ctx=self._ctx, is_async=is_async)
        self.utils = TonUtils(ctx=self._ctx, is_async=is_async)

    @property
    def is_async(self):
        return self._is_async

    @is_async.setter
    def is_async(self, value: bool):
        self._is_async = value
        self.base.is_async = value
        self.crypto.is_async = value
        self.net.is_async = value
        self.abi.is_async = value
        self.boc.is_async = value
        self.processing.is_async = value
        self.utils.is_async = value

    @property
    def version(self):
        return self.base.version

    @property
    def get_api_reference(self):
        return self.base.get_api_reference

    @staticmethod
    def create_context(config: Dict[str, Dict[str, Union[str, int, float]]]):
        response_ptr = tc_create_context(config=config)
        response = TCSyncResponseData(tc_read_string(string=response_ptr))
        is_success, result, error = (
            response.is_success, response.result, response.error)
        tc_destroy_string(response_ptr)

        if not is_success:
            raise TonException(error=error)

        return TCClientContext(result)

    def destroy_context(self):
        tc_destroy_context(ctx=self._ctx)
