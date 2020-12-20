from tonclient.bindings.lib import tc_create_context, tc_destroy_context, \
    tc_read_string, tc_destroy_string
from tonclient.bindings.types import TCClientContext, TCSyncResponseData
from tonclient.boc import TonBoc
from tonclient.debot import TonDebot
from tonclient.decorators import result_as
from tonclient.errors import TonException
from tonclient.module import TonModule
from tonclient.crypto import TonCrypto
from tonclient.net import TonNet
from tonclient.abi import TonAbi
from tonclient.processing import TonProcessing
from tonclient.tvm import TonTvm
from tonclient.types import ClientError, ClientConfig, ResultOfVersion, \
    ResultOfGetApiReference, ResultOfBuildInfo, ParamsOfResolveAppRequest
from tonclient.utils import TonUtils

DEVNET_BASE_URL = 'net.ton.dev'
MAINNET_BASE_URL = 'main.ton.dev'


class TonClientBase(TonModule):
    @result_as(classname=ResultOfVersion)
    def version(self) -> ResultOfVersion:
        """ Returns Core Library version """
        return self.request(method='client.version')

    @result_as(classname=ResultOfGetApiReference)
    def get_api_reference(self) -> ResultOfGetApiReference:
        """ Returns Core Library API reference """
        return self.request(method='client.get_api_reference')

    @result_as(classname=ResultOfBuildInfo)
    def build_info(self) -> ResultOfBuildInfo:
        return self.request(method='client.build_info')

    def resolve_app_request(self, params: ParamsOfResolveAppRequest):
        """ Resolves application request processing result """
        return self.request(
            method='client.resolve_app_request', **params.dict)


class TonClient(object):
    """ Main client class to create object of """
    def __init__(
            self, config: ClientConfig, is_core_async: bool = True,
            is_async: bool = False):
        """
        :param config: ClientConfig object
        :param is_core_async: Use sync or async core requests
        :param is_async: Client mode
        """
        super(TonClient, self).__init__()

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

    @property
    def ctx(self):
        return self._ctx

    @property
    def is_core_async(self):
        return self._is_core_async

    @property
    def is_async(self):
        return self._is_async

    @property
    def version(self):
        return self.base.version

    @property
    def get_api_reference(self):
        return self.base.get_api_reference

    @property
    def build_info(self):
        return self.base.build_info

    @property
    def resolve_app_request(self):
        return self.base.resolve_app_request

    @staticmethod
    def create_context(config: ClientConfig):
        response_ptr = tc_create_context(config=config.dict)
        response = TCSyncResponseData(tc_read_string(string=response_ptr))
        is_success, result, error = (
            response.is_success, response.result, response.error)
        tc_destroy_string(response_ptr)

        if not is_success:
            raise TonException(error=ClientError(**error))

        return TCClientContext(result)

    def destroy_context(self):
        tc_destroy_context(ctx=self._ctx)
