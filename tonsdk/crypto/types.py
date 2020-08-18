from __future__ import annotations
import json
from io import StringIO
from typing import Dict


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
    def load(path: str, is_binary: bool) -> KeyPair:
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
    def load_io(io: StringIO, as_binary: bool = False) -> KeyPair:
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


class NaclBox(object):
    OUTPUT_TEXT = "Text"
    OUTPUT_HEX = "Hex"
    OUTPUT_HEX_UP = "HexUppercase"
    OUTPUT_BASE64 = "Base64"

    def __init__(
            self, key: str, message: str, output: str = OUTPUT_HEX):
        """
        :param key: Key can be either secret or public, depending on situation
        :param message: Message string. Use one of 'as_' methods to prepare
                        message
        :param output: Box output format
        """
        self.key = key
        self.message = FmtString(message)
        self.output = output

    def as_text(self) -> NaclBox:
        """ Box message as FmtString.text """
        self.message = self.message.text
        return self

    def as_hex(self) -> NaclBox:
        """ Box message as FmtString.hex string """
        self.message = self.message.hex
        return self

    def as_base64(self) -> NaclBox:
        """ Box message as FmtString.base64 """
        self.message = self.message.base64
        return self
