import os
import ctypes
import json
import platform
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

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
    def __init__(self,lib_name=detect_lib()):
        self.lib_path = os.path.join(BASE_DIR, 'lib', 'libton_client.so')
        self.lib = ctypes.cdll.LoadLibrary(self.lib_path)

    def _request(self,method_name,params={}):
        lib = self.lib
        context = lib.tc_create_context()
        context = ctypes.c_uint32(context)
        print('Context: ', context)

        fn_name = method_name.encode()
        fn_interop = InteropString(
            ctypes.cast(fn_name, ctypes.c_char_p), len(fn_name))

        print('Fn name: ', fn_interop)

        data = json.dumps(params).encode()
        data_interop = InteropString(
            ctypes.cast(data, ctypes.c_char_p), len(data)
        )
        print('Data: ', data)

        lib.tc_json_request.restype = ctypes.POINTER(InteropJsonResponse)
        response = lib.tc_json_request(context, fn_interop, data_interop)
        print('Response: ', response)

        lib.tc_read_json_response.restype = InteropJsonResponse
        read = lib.tc_read_json_response(response)
        print('Read response: ', read)
        if read.result_json.len:
            print('Result JSON: ', read.result_json.content)
        elif read.error_json.len:
            print('Error JSON: ', read.error_json.content)

        lib.tc_destroy_json_response(response)
        lib.tc_destroy_context(context)


ton = TonClient()

ton._request('crypto.mnemonic.from.random')