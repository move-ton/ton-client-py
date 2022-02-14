"""Module with lib binding methods"""
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
    machine = platform.machine().lower()
    system = platform.system().lower()
    system_ext = {'windows': 'dll', 'darwin': 'dylib', 'linux': 'so'}
    ext = system_ext.get(system, '')

    # Try to load binary for system and machine type
    path = os.path.join(LIB_DIR, f'{LIB_FILENAME}.{machine}.{ext}')
    if os.path.exists(path):
        return path

    # Try to load library just for system
    fallback = os.path.join(LIB_DIR, f'{LIB_FILENAME}.{ext}')
    if not os.path.exists(fallback):
        raise RuntimeError(
            f'No library for machine `{machine}` and platform `{system}`'
        )
    return fallback


_LIB = ctypes.cdll.LoadLibrary(_get_lib_path())


def tc_create_context(
    config: Dict[str, Dict[str, Union[str, int, float]]]
) -> ctypes.POINTER(ctypes.c_char_p):
    """Create client context"""
    _config = TCStringData.from_string(string=json.dumps(config))

    _LIB.tc_create_context.restype = ctypes.POINTER(ctypes.c_char_p)
    return _LIB.tc_create_context(_config)


def tc_destroy_context(ctx: ctypes.c_int32):
    """Destroy client context"""
    _LIB.tc_destroy_context(ctx)


def tc_request(
    ctx: ctypes.c_int32,
    method: str,
    request_id: int,
    response_handler: TCResponseHandler,
    params_json: str = None,
):
    """Make async request"""
    # Cast args to ctypes
    method = TCStringData.from_string(string=method)
    request_id = ctypes.c_int32(request_id)
    params_json = TCStringData.from_string(string=params_json)

    _LIB.tc_request(ctx, method, params_json, request_id, response_handler)


def tc_request_sync(
    ctx: ctypes.c_int32, method: str, params_json: str = None
) -> ctypes.POINTER(ctypes.c_char_p):
    """Make sync request (might be deprecated)"""
    method = TCStringData.from_string(string=method)
    params_json = TCStringData.from_string(string=params_json)

    _LIB.tc_request_sync.restype = ctypes.POINTER(ctypes.c_char_p)
    return _LIB.tc_request_sync(ctx, method, params_json)


def tc_destroy_string(string: ctypes.POINTER(ctypes.c_char_p)):
    """Destroy string"""
    _LIB.tc_destroy_string(string)


def tc_read_string(string: ctypes.POINTER(ctypes.c_char_p)) -> TCStringData:
    """Read string"""
    _LIB.tc_read_string.restype = TCStringData
    return _LIB.tc_read_string(string)
