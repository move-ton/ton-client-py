import ctypes
import json


class TCStringT(ctypes.Structure):
    _fields_ = [
        ('content', ctypes.c_char_p),
        ('len', ctypes.c_int, 32)
    ]

    @staticmethod
    def from_string(string: str):
        string = string.encode()
        return TCStringT(ctypes.c_char_p(string), len(string))


class TCResponseT(ctypes.Structure):
    _fields_ = [
        ('result_json', TCStringT),
        ('error_json', TCStringT)
    ]

    def __str__(self):
        return self.content
    __repr__ = __str__

    @property
    def is_success(self):
        return bool(self.result_json.len)

    @property
    def len(self):
        return self.result_json.len if self.is_success else self.error_json.len

    @property
    def content(self):
        result = self.result_json if self.is_success else self.error_json
        return result.content.decode(errors='replace')[:self.len]

    @property
    def json(self):
        return json.loads(self.content)


# TODO: Research when and where it is used
# class TCResponseFlagsT(ctypes.Structure):
#     __fields__ = [
#         ("tc_response_finished", ctypes.c_int)
#     ]
#
#     def __init__(self):
#         super(TCResponseFlagsT, self).__init__()
#         self.tc_response_finished = 1


TCResponseTPointer = ctypes.POINTER(TCResponseT)
TCOnResponseT = ctypes.CFUNCTYPE(
    ctypes.c_void_p,
    ctypes.c_int32,
    TCStringT,
    TCStringT,
    ctypes.c_int32)
