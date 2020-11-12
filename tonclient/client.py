from typing import Dict, Union, Any

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
from tonclient.tvm import TonTvm
from tonclient.types import DEFAULT_MNEMONIC_DICTIONARY, \
    DEFAULT_MNEMONIC_WORD_COUNT, DEFAULT_HDKEY_DERIVATION_PATH
from tonclient.utils import TonUtils

DEVNET_BASE_URL = 'net.ton.dev'
MAINNET_BASE_URL = 'main.ton.dev'

CLIENT_DEFAULT_SETUP = {
    'network': {
        'server_address': 'http://localhost',
        'network_retries_count': 5,
        'message_retries_count': 5,
        'message_processing_timeout': 40000,
        'wait_for_timeout': 40000,
        'out_of_sync_threshold': 15000,
        'access_key': ''
    },
    'crypto': {
        'mnemonic_dictionary': DEFAULT_MNEMONIC_DICTIONARY,
        'mnemonic_word_count': DEFAULT_MNEMONIC_WORD_COUNT,
        'hdkey_derivation_path': DEFAULT_HDKEY_DERIVATION_PATH,
        'hdkey_compliant': True
    },
    'abi': {
        'workchain': 0,
        'message_expiration_timeout': 40000,
        'message_expiration_timeout_grow_factor': 1.5
    }
}


class TonClientBase(TonModule):
    @Response.version
    def version(self) -> str:
        """ Returns Core Library version """
        return self.request(method='client.version')

    @Response.get_api_reference
    def get_api_reference(self) -> Dict:
        """ Returns Core Library API reference """
        return self.request(method='client.get_api_reference')

    def build_info(self) -> Dict[str, Any]:
        return self.request(method='client.build_info')


class TonClient(object):
    """ Main client class to create object of """
    def __init__(
            self, network: Dict[str, Union[str, int]] = None,
            crypto: Dict[str, str] = None,
            abi: Dict[str, Union[int, float]] = None,
            is_core_async: bool = True, is_async: bool = False):
        """
        :param network: Client core network config
        :param crypto: Client core crypto config
        :param abi: Client core abi config
        :param is_core_async: Use sync or async core requests
        :param is_async: Client mode
        """
        super(TonClient, self).__init__()

        self._ctx = self.create_context(config={
            'network': {**CLIENT_DEFAULT_SETUP['network'], **(network or {})},
            'crypto': {**CLIENT_DEFAULT_SETUP['crypto'], **(crypto or {})},
            'abi': {**CLIENT_DEFAULT_SETUP['abi'], **(abi or {})}
        })
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

    @property
    def ctx(self):
        return self._ctx

    @property
    def is_core_async(self):
        return self._is_core_async

    @is_core_async.setter
    def is_core_async(self, value: bool):
        self._is_core_async = value

    @property
    def is_async(self):
        return self._is_async

    @is_async.setter
    def is_async(self, value: bool):
        self._is_async = value

    @property
    def version(self):
        return self.base.version

    @property
    def get_api_reference(self):
        return self.base.get_api_reference

    @property
    def build_info(self):
        return self.base.build_info

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
