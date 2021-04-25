import ctypes
import json
import os
import platform

from typing import Dict, Union

from .types import TCStringData, TCResponseHandler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
LIB_DIR = os.path.join(BASE_DIR, 'bin')
LIB_FILENAME = 'ton-rust-client'


def _get_lib_path():
    plt = platform.system().lower()
    lib_ext_dict = {
        'windows': 'dll',
        'darwin': 'dylib',
        'linux': 'so'
    }
    if plt not in lib_ext_dict:
        raise RuntimeError(
            f'No library for current platform "{plt.capitalize()}"')
    return os.path.join(LIB_DIR, f'{LIB_FILENAME}.{lib_ext_dict[plt]}')


_LIB = ctypes.cdll.LoadLibrary(_get_lib_path())


def tc_create_context(
        config: Dict[str, Dict[str, Union[str, int, float]]]
) -> ctypes.POINTER(ctypes.c_char_p):
    _config = TCStringData.from_string(string=json.dumps(config))

    _LIB.tc_create_context.restype = ctypes.POINTER(ctypes.c_char_p)
    return _LIB.tc_create_context(_config)


def tc_destroy_context(ctx: ctypes.c_int32):
    _LIB.tc_destroy_context(ctx)


def tc_request(
        ctx: ctypes.c_int32, method: str, request_id: int,
        response_handler: TCResponseHandler, params_json: str = None):
    # Cast args to ctypes
    method = TCStringData.from_string(string=method)
    request_id = ctypes.c_int32(request_id)
    params_json = TCStringData.from_string(string=params_json)

    _LIB.tc_request(
        ctx, method, params_json, request_id, response_handler)


def tc_request_sync(
        ctx: ctypes.c_int32, method: str, params_json: str = None
) -> ctypes.POINTER(ctypes.c_char_p):
    method = TCStringData.from_string(string=method)
    params_json = TCStringData.from_string(string=params_json)

    _LIB.tc_request_sync.restype = ctypes.POINTER(ctypes.c_char_p)
    return _LIB.tc_request_sync(ctx, method, params_json)


def tc_destroy_string(string: ctypes.POINTER(ctypes.c_char_p)):
    _LIB.tc_destroy_string(string)


def tc_read_string(string: ctypes.POINTER(ctypes.c_char_p)) -> TCStringData:
    _LIB.tc_read_string.restype = TCStringData
    return _LIB.tc_read_string(string)
