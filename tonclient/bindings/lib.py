import ctypes
import os
import platform

from .types import TCOnResponseT, TCStringT, TCResponseTPointer, TCResponseT

BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
LIB_VERSION = '0.25.3'
LIB_DIR = os.path.join(BASE_DIR, 'bin')
LIB_FILENAME = f'ton-rust-client-{LIB_VERSION}'


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


def tc_create_context() -> ctypes.c_int32:
    return _LIB.tc_create_context()


def tc_destroy_context(ctx: ctypes.c_int32):
    _LIB.tc_destroy_context(ctx)


def tc_json_request(
            ctx: ctypes.c_int32, method: str, params_json: str = None
        ) -> TCResponseTPointer:
    # Cast args to ctypes
    method = TCStringT.from_string(string=method)
    params_json = TCStringT.from_string(string=params_json)

    _LIB.tc_json_request.restype = TCResponseTPointer
    return _LIB.tc_json_request(ctx, method, params_json)


def tc_read_json_response(handle: TCResponseTPointer) -> TCResponseT:
    _LIB.tc_read_json_response.restype = TCResponseT
    return _LIB.tc_read_json_response(handle)


def tc_destroy_json_response(handle: TCResponseTPointer):
    _LIB.tc_destroy_json_response(handle)


def tc_json_request_async(
        ctx: ctypes.c_int32, method: str, request_id: int,
        callback: TCOnResponseT, params_json: str = None):
    # Cast args to ctypes
    method = TCStringT.from_string(string=method)
    request_id = ctypes.c_int32(request_id)
    params_json = TCStringT.from_string(string=params_json)

    _LIB.tc_json_request_async(ctx, method, params_json, request_id, callback)
