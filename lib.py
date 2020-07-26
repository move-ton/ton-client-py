import os
import ctypes
import json
import platform
import logging
import asyncio
from ton_types import *
from helpers import *
import time

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

OnResult = ctypes.CFUNCTYPE(
    ctypes.c_void_p, ctypes.c_int32, InteropString, InteropString,
    ctypes.c_int32)

def _on_result(request_id: int, result_json: InteropString,
               error_json: InteropString, flags: int):
    """ Python callback for lib async request """
    print('Async callback fired')
    print(f'Request ID: {request_id}\nResult JSON: {result_json}\n'
          f'Error JSON: {error_json}\nFlags: {flags}')

    if result_json.len > 0:
        print('Result JSON: ', result_json.content)
    elif error_json.len > 0:
        print('Error JSON: ', error_json.content)
    else:
        print('No response data')


class TonJsonResponse:
    result_json = None
    status = None # True - good, False - error
    context = None # ctypes.c_uint32

class TonClient:
    lib_path = None
    lib = None
    logging.basicConfig(level=logging.DEBUG)
    def __init__(self,path=BASE_DIR,lib_name=detect_lib()):
        logging.debug('Start new Session')
        self.lib_path = os.path.join(path, 'lib', lib_name)
        self.lib = ctypes.cdll.LoadLibrary(self.lib_path)

    def set_level_debugging(level):
        logging.basicConfig(filename='py-ton-sdk.log', filemode='a',level=level)

    def _create_context(self):
        context = self.lib.tc_create_context()  # Create ton context in rust
        return ctypes.c_uint32(context) # Convert context in uint32 

    def _destroy_context(self,context):
        self.lib.tc_destroy_context(context) # Destroy context
    
    async def _request_async(self, context, id, method, data=None,func=_on_result):
        lib = self.lib
        logging.debug(f'Context: {context}')

        method = method.encode()
        method_interop = InteropString(
            ctypes.cast(method, ctypes.c_char_p), len(method))
        logging.debug(f'Fn name: {method}')

        data = json.dumps(data or {}).encode()
        data_interop = InteropString(
            ctypes.cast(data, ctypes.c_char_p), len(data)
        )
        logging.debug(f'Data: {data}')

        on_result = OnResult(func)
        response = lib.tc_json_request_async(
            context, method_interop, data_interop, ctypes.c_int32(id), on_result)
        logging.debug(f'Response: {response}')

        lib.tc_destroy_json_response(response)
        lib.tc_destroy_context(context)
        return response

    def _request(self,context,method_name,params={}):
        logging.debug('Create request')
        lib = self.lib
        logging.debug(f'Context: {context}')
        fn_name = method_name.encode() #Encode method name in bytes
        fn_interop = InteropString(
            ctypes.cast(fn_name, ctypes.c_char_p), len(fn_name)) #Convert method name in InteropString

        logging.debug(f'Fn name: {fn_interop}')
        data = json.dumps(params).encode() # Convert params in string and encode this string in bytes
        data_interop = InteropString(
            ctypes.cast(data, ctypes.c_char_p), len(data) # Convert params in bytes 
        )
        logging.debug(f'Data: {data}')

        lib.tc_json_request.restype = ctypes.POINTER(InteropJsonResponse) # Set what tc_json_request return address of InteropJsonResponse
        response = lib.tc_json_request(context, fn_interop, data_interop) # Request
        logging.debug(f'Response: {response}')

        lib.tc_read_json_response.restype = InteropJsonResponse # Set what tc_read_json_response return InteropJsonResponse
        read = lib.tc_read_json_response(response) # Get InteropJsonResponse
        logging.debug(f'Read response: : {read}')
        obj = TonJsonResponse() 
        if read.result_json.len: # If noerror
            logging.debug(f'Result JSON: {read.result_json.content}')
            obj.result_json = read.result_json.content
            obj.status = True
        elif read.error_json.len: # If error 
            logging.warning(f'Error json response')
            logging.debug(f'Error JSON: {read.error_json.content}')
            obj.result_json = read.error_json.content
            obj.status = False
        obj.context = context
        lib.tc_destroy_json_response(response) # Destroy json response in memory
        return obj

