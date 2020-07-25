import ctypes
import json
import time
import base64
from json import JSONEncoder
from typing import NewType
from pydantic import BaseModel
#help(ctypes)
#help(ctypes.create_string_buffer(b"hello"))

class InteropString(ctypes.Structure):
    _fields_ = [("Content",	ctypes.c_char_p),  # u8
                ("Length", ctypes.c_uint)]  # u32


class InteropJsonResponse(ctypes.Structure):
    _fields_ = [("result_json", InteropString),
                ("error_json", InteropString)]


def string_to_InteropString(string):
    obj = InteropString()
    str_bytes = string.encode()
    obj.Content = ctypes.c_char_p(str_bytes)
    print(obj.Content)
    obj.Length = len(str_bytes)
    return obj

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



class TonClient():
    lib = None # ctypes.CDLL

    default_settings = {}

    def __init__(self, lib:str="./libton_client.so"):
        self.lib = ctypes.cdll.LoadLibrary(lib)

    def request(self,method_name,parametrs):

        id_context = self.lib.tc_create_context() # Create context
        id_context = ctypes.c_int(id_context) # Convert point context to int in c++

        # TODO: Вылетает нахрен почему то если parametrs не пустой
        self.lib.tc_json_request.restype = ctypes.POINTER(InteropJsonResponse) # Set what 'tc_json_request' return Point of 'InteropJsonResponse'
        print("a")
        id_json_request = self.lib.tc_json_request(id_context, string_to_InteropString( # Send to node json request with method name and parametrs
            method_name), string_to_InteropString(parametrs))
        self.lib.tc_read_json_response.restype = InteropJsonResponse # Set what 'tc_read_json_response' return  'InteropJsonResponse'
        response = self.lib.tc_read_json_response(id_json_request) # Read json response
        print("a")
        self.lib.tc_destroy_json_response(id_json_request) # Delete json response in library for availibity reading Content in Json
        # TODO: Detect error or result

        print(response.error_json,"a") 
        print(response.result_json) 
        self.lib.tc_destroy_context(id_context) # Destroy context


# Test

ton = TonClient()

ton.request("Setup",'{"wait_for_timeout":50000}')