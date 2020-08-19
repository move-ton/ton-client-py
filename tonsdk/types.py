import json
from io import StringIO
from typing import Dict, Any

NACL_OUTPUT_TXT = "Text"
NACL_OUTPUT_HEX = "Hex"
NACL_OUTPUT_HEX_UP = "HexUppercase"
NACL_OUTPUT_B64 = "Base64"


class KeyPair(object):
    """ Keypair object representation """
    def __init__(self, public: str, secret: str):
        self.public = public
        self.secret = secret

    @property
    def dict(self) -> Dict[str, str]:
        return {"public": self.public, "secret": self.secret}

    @property
    def binary(self) -> bytes:
        return bytes.fromhex(f"{self.secret}{self.public}")

    @staticmethod
    def load(path: str, is_binary: bool) -> "KeyPair":
        """ Load keypair from file """
        if is_binary:
            with open(path, "rb") as fp:
                keys = fp.read().hex()
                keys = {"public": keys[64:], "secret": keys[:64]}
        else:
            with open(path, "r") as fp:
                keys = json.loads(fp.read())

        return KeyPair(**keys)

    def dump(self, path: str, as_binary: bool) -> None:
        """ Dump keypair to file """
        if as_binary:
            with open(path, "wb") as fp:
                fp.write(self.binary)
        else:
            with open(path, "w") as fp:
                json.dump(self.dict, fp)

    @staticmethod
    def load_io(io: StringIO, as_binary: bool = False) -> "KeyPair":
        """ Load keypair from StringIO """
        data = io.getvalue()
        keys = json.loads(data) \
            if not as_binary else {"public": data[64:], "secret": data[:64]}

        return KeyPair(**keys)

    def dump_io(self, io: StringIO, as_binary: bool = False):
        """ Dump keypair to StringIO """
        keys = json.dumps(self.dict) if not as_binary else self.binary.hex()
        io.write(keys)


class FmtString(str):
    """ Formatted string for requests """
    @property
    def text(self) -> Dict[str, str]:
        return {"text": self}

    @property
    def hex(self) -> Dict[str, str]:
        return {"hex": self}

    @property
    def base64(self) -> Dict[str, str]:
        return {"base64": self}


class TonMessage(object):
    """ TON message """
    def __init__(
            self, message_id: str, address: str, body_b64: str,
            expire: int = None):
        self.address = address
        self.id = message_id
        self.body = body_b64
        self.expire = expire

    @property
    def to_request(self):
        return {
            "address": self.address,
            "messageId": self.id,
            "messageBodyBase64": self.body,
            "expire": self.expire
        }

    @staticmethod
    def from_response(response: Dict[str, Any]) -> "TonMessage":
        return TonMessage(
            message_id=response["messageId"], address=response["address"],
            body_b64=response["messageBodyBase64"], expire=response["expire"])


class TonUnsignedMessage(object):
    """ TON unsigned message """
    def __init__(
            self, unsigned_b64: str, sign_b64: str, expire: int = None,
            address: str = None):
        self.unsigned = unsigned_b64
        self.sign = sign_b64
        self.expire = expire
        self.address = address

    @property
    def to_request(self):
        return {
            "unsignedBytesBase64": self.unsigned,
            "signBytesBase64": self.sign,
            "expire": self.expire
        }

    @staticmethod
    def from_response(response: Dict[str, Any]) -> "TonUnsignedMessage":
        return TonUnsignedMessage(
            unsigned_b64=response["unsignedBytesBase64"],
            sign_b64=response["bytesToSignBase64"],
            expire=response["expire"])
