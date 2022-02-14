"""Library binding types"""
import ctypes
import json


class TCStringData(ctypes.Structure):
    """TCStringData"""

    _fields_ = [('content', ctypes.c_char_p), ('len', ctypes.c_int32)]

    @property
    def string(self):
        """Response as string"""
        if self.len:
            return self.content[: self.len].decode(errors='replace')
        return None

    @property
    def json(self):
        """Response as JSON"""
        if self.string:
            return json.loads(self.string)
        return None

    @staticmethod
    def from_string(string: str):
        """StringData from string"""
        string = string.encode()
        return TCStringData(ctypes.c_char_p(string), len(string))

    def __str__(self):
        return self.string

    __repr__ = __str__


class TCSyncResponseData(ctypes.Structure):
    """TCSyncResponseData"""

    _fields_ = [('string_data', TCStringData)]

    @property
    def is_success(self):
        """Request status"""
        return not self.error

    @property
    def result(self):
        """Parsed response result"""
        return self.string_data.json.get('result')

    @property
    def error(self):
        """Parsed request error"""
        return self.string_data.json.get('error')

    def __str__(self):
        return self.string_data.__str__()

    __repr__ = __str__


class TCResponseType:
    """Response types"""

    Success = 0
    Error = 1
    Nop = 2
    AppRequest = 3
    AppNotify = 4
    Custom = 100


TCClientContext = ctypes.c_int32
TCResponseHandler = ctypes.CFUNCTYPE(
    ctypes.c_void_p, ctypes.c_int32, TCStringData, ctypes.c_int32, ctypes.c_bool
)
