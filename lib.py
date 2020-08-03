import ctypes
import os
import json
import logging
import platform
from typing import Dict

from ton_types import InteropString, InteropJsonResponse

logger = logging.getLogger('ton')

BASE_DIR = os.path.dirname(__file__)
LIB_VERSION = '0.25.0'
LIB_DIR = os.path.join(BASE_DIR, 'bin')
LIB_FILENAME = f'ton-rust-client-{LIB_VERSION}'

DEVNET_BASE_URL = 'net.ton.dev'
MAINNET_BASE_URL = 'main.ton.dev'
TON_CLIENT_DEFAULT_SETUP = {
    'baseUrl': DEVNET_BASE_URL,
    'messageRetriesCount': 5,
    'messageExpirationTimeout': 10000,
    'messageExpirationTimeoutGrowFactor': 1.5,
    'messageProcessingTimeout': 30000,
    'messageProcessingTimeoutGrowFactor': 1.5,
    'waitForTimeout': 20000,
    'accessKey': ''
}


def get_lib_basename():
    plt = platform.system().lower()
    lib_ext_dict = {
        'windows': 'dll',
        'darwin': 'dylib',
        'linux': 'so'
    }
    if plt not in lib_ext_dict:
        raise RuntimeError(f'No library for current platform "{plt.capitalize()}"')
    return os.path.join(BASE_DIR, LIB_DIR, f'{LIB_FILENAME}.{lib_ext_dict[plt]}')


class TonClient(object):
    lib = None

    def __init__(self, lib_path: str = get_lib_basename()):
        logger.debug('Start new Session')
        self.lib = ctypes.cdll.LoadLibrary(lib_path)

        self.context = self._create_context()

    def setup(self, settings=None):
        settings = settings or TON_CLIENT_DEFAULT_SETUP
        return self._request("setup", settings)

    def version(self):
        return self._request("version", {})

    def _create_context(self):
        """ Create client context """
        context = self.lib.tc_create_context()
        return ctypes.c_uint32(context)

    def _destroy_context(self, context):
        """ Destroy client context """
        self.lib.tc_destroy_context(context)

    def _request(self, method_name, params: Dict) -> Dict:
        logger.debug('Create request')
        logger.debug(f'Context: {self.context}')

        method = method_name.encode()
        method_interop = InteropString(ctypes.cast(method, ctypes.c_char_p), len(method))
        logger.debug(f'Fn name: {method}')
        
        params = json.dumps(params).encode()
        params_interop = InteropString(ctypes.cast(params, ctypes.c_char_p), len(params))
        logger.debug(f'Data: {params}')

        self.lib.tc_json_request.restype = ctypes.POINTER(InteropJsonResponse)
        response = self.lib.tc_json_request(self.context, method_interop, params_interop)
        logger.debug(f'Response ptr: {response}')

        self.lib.tc_read_json_response.restype = InteropJsonResponse
        read = self.lib.tc_read_json_response(response)
        is_success = read.is_success
        response_json = read.json

        logger.debug(f'Read response: : {read}')
        logger.debug(f'Is success: {is_success}')

        self.lib.tc_destroy_json_response(response)
        return {
            'success': is_success, 'result': response_json
        }

    # async def _request_async(self, method_name, params: Dict, req_id: int, cb: Callable = _on_result):
    #     logger.debug('Create request (async)')
    #     logger.debug(f'Context: {self.context}')
    #
    #     method = method_name.encode()
    #     method_interop = InteropString(ctypes.cast(method, ctypes.c_char_p), len(method))
    #     logger.debug(f'Fn name: {method}')
    #
    #     params = json.dumps(params).encode()
    #     params_interop = InteropString(
    #         ctypes.cast(params, ctypes.c_char_p), len(params)
    #     )
    #     logger.debug(f'Data: {params}')
    #
    #     on_result = OnResult(cb)
    #     response = self.lib.tc_json_request_async(
    #         self.context, method_interop, params_interop, ctypes.c_int32(req_id), on_result)
    #     logger.debug(f'Response: {response}')
    #
    #     self.lib.tc_destroy_json_response(response)
    #     return response


# def _on_result(
#         request_id: int,
#         result_json: InteropString,
#         error_json: InteropString, flags: int):
#     """ Python callback for lib async request """
#     logger.debug('Async callback fired')
#     logger.debug(
#         f'Request ID: {request_id}\n'
#         f'Result JSON: {result_json}\n'
#         f'Error JSON: {error_json}\n'
#         f'Flags: {flags}\n')
#
#     if result_json.len > 0:
#         logger.debug('Result JSON: ', result_json.content)
#     elif error_json.len > 0:
#         logger.debug('Error JSON: ', error_json.content)
#     else:
#         logger.debug('No response data')
