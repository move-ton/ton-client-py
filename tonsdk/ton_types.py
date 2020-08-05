import ctypes
import json


class InteropString(ctypes.Structure):
    _fields_ = [
        ('content', ctypes.c_char_p),
        ('len', ctypes.c_int, 32)
    ]

    @staticmethod
    def from_string(string: str):
        string = string.encode()
        return InteropString(ctypes.c_char_p(string), len(string))


class InteropJsonResponse(ctypes.Structure):
    _fields_ = [
        ('result_json', InteropString),
        ('error_json', InteropString)
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


ResultCb = ctypes.CFUNCTYPE(
    ctypes.c_void_p,
    ctypes.c_int32,
    ctypes.POINTER(InteropString),
    ctypes.POINTER(InteropString),
    ctypes.c_int32)
