from typing import Dict

from .lib import TonClient
from .types import KeyPair, FmtString


class TonCrypto(object):
    """ Free TON crypto SDK implementation """
    def __init__(self, client: TonClient):
        self._client = client

    def random_generate_bytes(self, length: int) -> str:
        """
        :param length:
        :return: str
        """
        params = {"length": length}
        return self._client.request(
            method="crypto.random.generateBytes", params=params)

    def derive_sign_keys(self, mnemonic: str) -> KeyPair:
        """
        :param mnemonic: Mnemonic phrase
        :return: KeyPair object
        """
        params = {"phrase": mnemonic, "wordCount": len(mnemonic.split(" "))}
        response = self._client.request(
            method="crypto.mnemonic.derive.sign.keys", params=params)

        return KeyPair(**response)

    def ton_crc16(self, fmt_string: Dict) -> int:
        """
        :param fmt_string: One of FmtString properties
        :return:
        """
        return self._client.request(
            method='crypto.ton_crc16', params=fmt_string)
