import platform
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