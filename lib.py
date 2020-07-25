import os
import ctypes
import json
import platform
import logging
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
logging.basicConfig(filename='py-ton-sdk.log', filemode='a', level=logging.DEBUG)
class InteropString(ctypes.Structure):
    _fields_ = [
        ('content', ctypes.c_char_p),
        ('len', ctypes.c_int, 32)
    ]


class InteropJsonResponse(ctypes.Structure):
    _fields_ = [
        ('result_json', InteropString),
        ('error_json', InteropString)
    ]

class TonJsonResponse:
    result_json = None
    status = None # True - good, False - error

def detect_lib():
    plt = platform.system()
    if plt == "Windows":
        return 'libton_client.dll'
    elif plt == "Darwin":
        return 'libton_client.dylib'
    else:
        return 'libton_client.so'

        
class TonJsonSettings:
    # Hint
    base_url = "net.ton.dev"#Url node
    message_retries_count = 5 
    message_expiration_timeout = 10000
    message_expiration_timeout_grow_factor = 1.5
    message_processing_timeout = 40000
    message_processing_timeout_grow_factor = 1.5
    wait_for_timeout = 40000
    access_key = ""
    def __init__(self,**kwargs):
        self.__dict__.update(kwargs)

class TonClient:
    lib_path = None
    lib = None
    logging.basicConfig(level=logging.DEBUG)
    def __init__(self,lib_name=detect_lib()):
        logging.debug('Start new Session')
        self.lib_path = os.path.join(BASE_DIR, 'lib', 'libton_client.so')
        self.lib = ctypes.cdll.LoadLibrary(self.lib_path)

    def set_level_debugging(level):
        logging.basicConfig(filename='py-ton-sdk.log', filemode='a',level=level)

    def _request(self,method_name,params={}):
        logging.debug('Create request')
        lib = self.lib
        context = lib.tc_create_context()
        context = ctypes.c_uint32(context)
        logging.debug(f'Context: {context}')
        fn_name = method_name.encode()
        fn_interop = InteropString(
            ctypes.cast(fn_name, ctypes.c_char_p), len(fn_name))

        logging.debug(f'Fn name: {fn_interop}')
        data = json.dumps(params).encode()
        data_interop = InteropString(
            ctypes.cast(data, ctypes.c_char_p), len(data)
        )
        logging.debug(f'Data: {data}')

        lib.tc_json_request.restype = ctypes.POINTER(InteropJsonResponse)
        response = lib.tc_json_request(context, fn_interop, data_interop)
        logging.debug(f'Response: {response}')

        lib.tc_read_json_response.restype = InteropJsonResponse
        read = lib.tc_read_json_response(response)
        logging.debug(f'Read response: : {read}')
        resp = TonJsonResponse()
        if read.result_json.len:
            logging.debug(f'Result JSON: {read.result_json.content}')
            resp.result_json = read.result_json.content
            resp.status = True
        elif read.error_json.len:
            logging.warning(f'Error json response')
            logging.debug(f'Error JSON: {read.error_json.content}')
            resp.result_json = read.error_json.content
            resp.status = False

        lib.tc_destroy_json_response(response)
        lib.tc_destroy_context(context)
        return resp
        
        
        return 

ton = TonClient()

ton._request('crypto.mnemonic.from.random')