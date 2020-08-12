import json
from typing import Dict

from tonsdk.errors import TonException


class KeyPair:
    """ Keypair object representation """
    def __init__(self, public: str, secret: str):
        self.public = public
        self.secret = secret

    @property
    def as_dict(self) -> Dict[str, str]:
        return {"public": self.public, "secret": self.secret}

    @property
    def as_binary(self) -> bytes:
        return bytes.fromhex(f"{self.secret}{self.public}")

    @staticmethod
    def load(path: str, is_binary: bool) -> object:
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
                fp.write(self.as_binary)
        else:
            with open(path, "w") as fp:
                json.dump(self.as_dict, fp)


class FmtString:
    """ Formatted string for requests """
    def __init__(self, string: str):
        self.string = string

    def __getattr__(self, item):
        if item not in ["as_text", "as_hex", "as_base64"]:
            raise TonException(
                "String format should be one of 'as_text, as_hex, as_base64'")

        return {item.replace("as_", ""): self.string}
