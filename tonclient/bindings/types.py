import ctypes
import json


class TCStringData(ctypes.Structure):
    _fields_ = [
        ('content', ctypes.c_char_p),
        ('len', ctypes.c_int32)
    ]

    @property
    def string(self):
        return self.content.decode(errors='replace')[:self.len]

    @property
    def json(self):
        return json.loads(self.string)

    @staticmethod
    def from_string(string: str):
        string = string.encode()
        return TCStringData(ctypes.c_char_p(string), len(string))

    def __str__(self):
        return self.string
    __repr__ = __str__


class TCSyncResponseData(ctypes.Structure):
    _fields_ = [
        ('string_data', TCStringData)
    ]

    @property
    def is_success(self):
        return not self.error

    @property
    def result(self):
        return self.string_data.json.get('result')

    @property
    def error(self):
        return self.string_data.json.get('error')

    def __str__(self):
        return self.string_data.__str__()
    __repr__ = __str__


class TCResponseType(object):
    Success = 0
    Error = 1
    Nop = 2
    Custom = 100


TCClientContext = ctypes.c_int32
TCResponseHandler = ctypes.CFUNCTYPE(
    ctypes.c_void_p, ctypes.c_int32, TCStringData, ctypes.c_int32,
    ctypes.c_bool)
