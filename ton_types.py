import ctypes

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