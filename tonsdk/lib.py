import ctypes
import os
import json
import logging
import platform
from typing import Dict

from tonsdk.ton_types import InteropString, InteropJsonResponse

logger = logging.getLogger('ton')

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
LIB_VERSION = '0.25.3'
LIB_DIR = os.path.join(BASE_DIR, 'bin')
LIB_FILENAME = f'ton-rust-client-{LIB_VERSION}'

DEVNET_BASE_URL = 'net.ton.dev'
MAINNET_BASE_URL = 'main.ton.dev'

TON_CLIENT_DEFAULT_SETUP = {
    'servers': ['http://localhost'],
    'messageRetriesCount': 1,
    'messageExpirationTimeout': 50000,
    'messageExpirationTimeoutGrowFactor': 1.5,
    'messageProcessingTimeout': 50000,
    'messageProcessingTimeoutGrowFactor': 1.5,
    'waitForTimeout': 30000,
    'accessKey': ''
}


def _get_lib_path():
    plt = platform.system().lower()
    lib_ext_dict = {
        'windows': 'dll',
        'darwin': 'dylib',
        'linux': 'so'
    }
    if plt not in lib_ext_dict:
        raise RuntimeError(
            f'No library for current platform "{plt.capitalize()}"')
    return os.path.join(LIB_DIR, f'{LIB_FILENAME}.{lib_ext_dict[plt]}')


_LIB = ctypes.cdll.LoadLibrary(_get_lib_path())


class TonClient(object):
    TYPE_TEXT = "text"
    TYPE_HEX = "hex"
    TYPE_BASE64 = "base64"

    BOX_OUTPUT_TEXT = "Text"
    BOX_OUTPUT_HEX = "Hex"
    BOX_OUTPUT_HEX_UP = "HexUppercase"
    BOX_OUTPUT_BASE64 = "Base64"

    def __init__(self, **config):
        self.context = _LIB.tc_create_context()
        self.setup({**TON_CLIENT_DEFAULT_SETUP, **config})

    def _request(self, method_name, params=None) -> Dict:
        """
        Args:
            method_name (str): SDK method name
            params (any): Method params
        Returns:
            dict
        """
        method_name = InteropString.from_string(method_name)
        params = InteropString.from_string(json.dumps(params or {}))

        _LIB.tc_json_request.restype = ctypes.POINTER(InteropJsonResponse)
        response_ptr = _LIB.tc_json_request(self.context, method_name, params)

        _LIB.tc_read_json_response.restype = InteropJsonResponse
        response = _LIB.tc_read_json_response(response_ptr)
        result = {'success': response.is_success, 'result': response.json}

        _LIB.tc_destroy_json_response(response_ptr)
        return result

    def destroy_context(self):
        return _LIB.tc_destroy_context(self.context)

    def setup(self, settings):
        return self.request(method="setup", params=settings)

    def version(self):
        return self.request(method="version")

    def _str_type_dict(self, string: str, fmt: str) -> Dict:
        """
        Generates dict for API params, based on string format
        Args:
            string (str): Any string
            fmt (str): One of 'TYPE_x' constants
        Returns:
            dict
        """
        if fmt not in [self.TYPE_BASE64, self.TYPE_HEX, self.TYPE_TEXT]:
            raise ValueError("One of 'base64, hex, text' should be provided for 'fmt' param")
        return {fmt: string}

    def request(self, method: str, params=None, raise_exception=True):
        result = self._request(method, params)

        if raise_exception and not result["success"]:
            raise Exception(result["result"])

        return result["result"]

    def random_generate_bytes(self, length: int) -> str:
        """
        Args:
            length (int):
        Returns:
            str
        """
        params = {"length": length}
        return self.request(
            method="crypto.random.generateBytes", params=params)

    def derive_sign_keys(self, mnemonic: str) -> Dict:
        """
        Args:
            mnemonic (str): Mnemonic phrase
        Returns:
            dict
        """
        params = {"phrase": mnemonic, "wordCount": len(mnemonic.split(" "))}
        return self.request(
            method="crypto.mnemonic.derive.sign.keys", params=params)

    def ton_crc16(self, string: str, string_fmt: str) -> int:
        """
        Args:
            string (str): String as hex, base64 or plain text
            string_fmt (str): String type ('TonClient.TYPE_x' constants)
        Returns:
            int
        """
        params = self._str_type_dict(string=string, fmt=string_fmt)
        return self.request(method='crypto.ton_crc16', params=params)

    def mnemonic_generate(self, word_count=24) -> str:
        """
        Generate random mnemonic
        Args:
            word_count (int):
        Returns:
            str
        """
        params = {"wordCount": word_count}
        return self.request(
            method='crypto.mnemonic.from.random', params=params)

    def mnemonic_from_entropy(self, entropy: str, entropy_fmt: str, word_count=24) -> str:
        """
        Args:
            entropy (str): String as hex, base64 or plain text
            entropy_fmt (str): Entropy string type (TonClient.TYPE_x)
            word_count (int):
        Returns:
            str
        """
        params = {
            "wordCount": word_count,
            "entropy": self._str_type_dict(string=entropy, fmt=entropy_fmt)
        }
        return self.request(
            method="crypto.mnemonic.from.entropy", params=params)

    def mnemonic_verify(self, mnemonic) -> bool:
        """
        Args:
            mnemonic (str):
        Returns:
            bool
        """
        params = {"phrase": mnemonic, "wordCount": len(mnemonic.split(" "))}
        return self.request(method='crypto.mnemonic.verify', params=params)

    def mnemonic_words(self) -> str:
        return self.request("crypto.mnemonic.words")

    def sha512(self, string: str, string_fmt: str) -> str:
        """
        Args:
            string (str): String as hex, base64 or plain text
            string_fmt (str): String type (TonClient.TYPE_x)
        Returns:
            str
        """
        params = {
            "message": self._str_type_dict(string=string, fmt=string_fmt)
        }
        return self.request(method='crypto.sha512', params=params)

    def sha256(self, string: str, string_fmt: str) -> str:
        """
        Args:
            string (str): String as hex, base64 or plain text
            string_fmt (str): Entropy string type (TonClient.TYPE_x)
        Returns:
            str
        """
        params = {
            "message": self._str_type_dict(string=string, fmt=string_fmt)
        }
        return self.request(method='crypto.sha256', params=params)

    def scrypt(
            self, data: str, n: int, r: int, p: int, dk_len: int, salt: str,
            salt_fmt: str, password: str, password_fmt: str) -> str:
        """
        Args:
            data (str): Data to encrypt
            n (int): The CPU/Memory cost parameter. Must be larger than 1,
                    a power of 2, and less than 2^(128 * r / 8)
            r (int): The parameter specifies block size
            p (int): The parallelization parameter. Is a positive integer
                    less than or equal to ((2^32-1) * 32) / (128 * r)
            dk_len (int): The intended output length. Is the length in octets
                    of the key to be derived ("keyLength"); it is a positive
                    integer less than or equal to (2^32 - 1) * 32.
            salt (str): Salt string
            salt_fmt (str): Salt string type (TonClient.TYPE_x)
            password (str): Password string
            password_fmt (str): Password string type (TonClient.TYPE_x)
        Returns:
            str
        """
        params = {
            "data": data,
            "salt": self._str_type_dict(string=salt, fmt=salt_fmt),
            "password": self._str_type_dict(string=password, fmt=password_fmt),
            "logN": n,
            "r": r,
            "p": p,
            "dkLen": dk_len
        }
        return self.request(method="crypto.scrypt", params=params)

    def keystore_add(self, keypair: Dict) -> str:
        """
        Args:
            keypair (dict): Keypair dict {"public": str, "secret": str}
        Returns:
            str: index in store
        """
        return self.request(method='crypto.keystore.add', params=keypair)

    def keystore_remove(self, index):
        """
        Args:
            index (str, int): Keystore index to be removed
        Returns:
            None or exception
        """
        self.request(method='crypto.keystore.remove', params=str(index))

    def keystore_clear(self):
        """ Clear keystore """
        self.request(method='crypto.keystore.clear')

    def hdkey_xprv_from_mnemonic(self, mnemonic: str) -> str:
        """
        Get BIP32 key from mnemonic
        Args:
            mnemonic (str):
        Returns:
            str
        """
        params = {"phrase": mnemonic, "wordCount": len(mnemonic.split(" "))}
        return self.request(
            method='crypto.hdkey.xprv.from.mnemonic', params=params)

    def hdkey_xprv_secret(self, bip32_key: str) -> str:
        """
        Get private key from BIP32 key
        Args:
            bip32_key (str):
        Returns:
            str
        """
        params = {"serialized": bip32_key}
        return self.request(method='crypto.hdkey.xprv.secret', params=params)

    def hdkey_xprv_public(self, bip32_key: str) -> str:
        """
        Get public key from BIP32 key
        Args:
            bip32_key (str):
        Returns:
            str
        """
        params = {"serialized": bip32_key}
        return self.request(method='crypto.hdkey.xprv.public', params=params)

    def hdkey_xprv_derive_path(self, bip32_key: str, derive_path: str) -> str:
        """
        Args:
            bip32_key (str):
            derive_path (str):
        Returns:
            str
        """
        params = {"serialized": bip32_key, 'path': derive_path}
        return self.request(
            method='crypto.hdkey.xprv.derive.path', params=params)

    def hdkey_xprv_derive(self, bip32_key: str, index: int) -> str:
        """
        Args:
            bip32_key (str):
            index (int):
        Returns:
            str
        """
        params = {"serialized": bip32_key, 'index': index}
        return self.request(method='crypto.hdkey.xprv.derive', params=params)

    def factorize(self, number: str) -> Dict:
        """
        Args:
            number (str):
        Returns:
            dict
        """
        return self.request(method='crypto.math.factorize', params=number)

    def ton_public_key_string(self, public_key: str) -> str:
        """
        Args:
            public_key (str):
        Returns:
            str
        """
        return self.request(
            method='crypto.ton_public_key_string', params=public_key)

    def ed25519_keypair(self) -> Dict:
        """ Generate ed25519 keypair """
        return self.request(method='crypto.ed25519.keypair')

    def modular_power(self, base: str, exponent: str, modulus: str) -> str:
        """
        Args:
            base (str):
            exponent (str):
            modulus (str):
        Returns:
            str
        """
        params = {'base': base, 'exponent': exponent, 'modulus': modulus}
        return self.request(method='crypto.math.modularPower', params=params)

    def nacl_box_keypair(self) -> Dict:
        """ Generate nacl box keypair """
        return self.request(method='crypto.nacl.box.keypair')

    def nacl_sign_keypair(self) -> Dict:
        """ Generate nacl sign keypair """
        return self.request(method='crypto.nacl.sign.keypair')

    def nacl_sign_keypair_from_secret_key(self, secret_key: str) -> Dict:
        """
        Generate nacl sign keypair from secret key
        Args:
            secret_key (str):
        Returns:
            dict
        """
        return self.request(
            method='crypto.nacl.sign.keypair.fromSecretKey', params=secret_key)

    def nacl_box_keypair_from_secret_key(self, key: str) -> Dict:
        return self.request(
            method='crypto.nacl.box.keypair.fromSecretKey', params=key)

    def nacl_box(
            self, nonce: str, their_public: str, secret_key: str, message: str,
            message_fmt: str, output_fmt: str = BOX_OUTPUT_HEX) -> str:
        """
        Args:
            nonce (str):
            their_public (str):
            secret_key (str):
            message (str): Message as hex, base64 or plain text
            message_fmt (str): Message string type (TonClient.TYPE_x)
            output_fmt (str):
        Returns:
            str
        """
        params = {
            "nonce": nonce,
            "theirPublicKey": their_public,
            "secretKey": secret_key,
            "message": self._str_type_dict(string=message, fmt=message_fmt),
            "outputEncoding": output_fmt
        }
        return self.request(method="crypto.nacl.box", params=params)

    def nacl_box_open(
            self, nonce: str, their_public: str, secret_key: str,
            message: str, message_fmt: str, output_fmt: str = BOX_OUTPUT_TEXT)\
            -> str:
        """
        Args:
            nonce (str):
            their_public (str):
            secret_key (str):
            message (str): Message as hex, base64 or plain text
            message_fmt (str): Message string type (TonClient.TYPE_x)
            output_fmt (str): Output format for opened message
        Returns:
            str
        """
        params = {
            "nonce": nonce,
            "theirPublicKey": their_public,
            "secretKey": secret_key,
            "message": self._str_type_dict(string=message, fmt=message_fmt),
            "outputEncoding": output_fmt
        }
        return self.request(method="crypto.nacl.box.open", params=params)

    def nacl_sign(
            self, key: str, message: str, message_fmt: str,
            output_fmt: str = BOX_OUTPUT_HEX) -> str:
        """
        Args:
            key (str):
            message (str): Message as hex, base64 or plain text
            message_fmt (str): Message string type (TonClient.TYPE_x)
            output_fmt (str):
        Returns:
            str
        """
        params = {
            "key": key,
            "message": self._str_type_dict(string=message, fmt=message_fmt),
            "outputEncoding": output_fmt
        }
        return self.request(method='crypto.nacl.sign', params=params)

    def nacl_sign_detached(
            self, key: str, message: str, message_fmt: str,
            output_fmt: str = BOX_OUTPUT_HEX) -> str:
        """
        Args:
            key (str):
            message (str): Message as hex, base64 or plain text
            message_fmt (str): Message string type (TonClient.TYPE_x)
            output_fmt (str):
        Returns:
            str
        """
        params = {
            "key": key,
            "message": self._str_type_dict(string=message, fmt=message_fmt),
            "outputEncoding": output_fmt
        }
        return self.request(method="crypto.nacl.sign.detached", params=params)

    def nacl_sign_open(
            self, key: str, message: str, message_fmt: str,
            output_fmt: str = BOX_OUTPUT_HEX) -> str:
        """
        Args:
            key (str):
            message (str): Message as hex, base64 or plain text
            message_fmt (str): Message string type (TonClient.TYPE_x)
            output_fmt (str):
        Returns:
            str
        """
        params = {
            "key": key,
            "message": self._str_type_dict(string=message, fmt=message_fmt),
            "outputEncoding": output_fmt
        }
        return self.request(method="crypto.nacl.sign.open", params=params)

    def nacl_secret_box(
            self, nonce: str, their_public: str, message: str,
            message_fmt: str, output_fmt: str = BOX_OUTPUT_HEX) -> str:
        """
        Args:
            nonce (str):
            their_public (str):
            message (str): Message as hex, base64 or plain text
            message_fmt (str): Message string type (TonClient.TYPE_x)
            output_fmt (str)
        Returns:
            str
        """
        params = {
            "nonce": nonce,
            "key": their_public,
            "message": self._str_type_dict(string=message, fmt=message_fmt),
            "outputEncoding": output_fmt
        }
        return self.request(method="crypto.nacl.secret.box", params=params)

    def nacl_secret_box_open(
            self, nonce: str, their_public: str, secret_key: str,
            message: str, message_fmt: str, output_fmt: str = BOX_OUTPUT_TEXT)\
            -> str:
        """
        Args:
            nonce (str):
            their_public (str):
            secret_key (str):
            message (str): Message as hex, base64 or plain text
            message_fmt (str): Message string type (TonClient.TYPE_x)
            output_fmt (str):
        Returns:
            str
        """
        params = {
            "nonce": nonce,
            "key": their_public,
            "secretKey": secret_key,
            "message": self._str_type_dict(string=message, fmt=message_fmt),
            "outputEncoding": output_fmt
        }
        return self.request(
            method="crypto.nacl.secret.box.open", params=params)

    # async def _request_async(self, method_name, params: Dict, req_id: int,
    #                          cb: Callable = _on_result):
    #     logger.debug('Create request (async)')
    #     logger.debug(f'Context: {self.context}')
    #
    #     method = method_name.encode()
    #     method_interop = InteropString(
    #         ctypes.cast(method, ctypes.c_char_p), len(method))
    #     logger.debug(f'Fn name: {method}')
    #
    #     params = json.dumps(params).encode()
    #     params_interop = InteropString(
    #         ctypes.cast(params, ctypes.c_char_p), len(params)
    #     )
    #     logger.debug(f'Data: {params}')
    #
    #     on_result = OnResult(cb)
    #     response = _LIB.tc_json_request_async(
    #         self.context, method_interop, params_interop,
    #         ctypes.c_int32(req_id), on_result)
    #     logger.debug(f'Response: {response}')
    #
    #     _LIB.tc_destroy_json_response(response)
    #     return response


# def _on_result(request_id: int, result_json: InteropString,
#                error_json: InteropString, flags: int):
#     """ Python callback for lib async request """
#     logger.debug('Async callback fired')
#     logger.debug(
#         f'Request ID: {request_id}\n'
#         f'Result JSON: {result_json}\n'
#         f'Error JSON: {error_json}\n'
#         f'Flags: {flags}\n')
#
#     if result_json.len > 0:
#         logger.debug('Result JSON: ', result_json.content)
#     elif error_json.len > 0:
#         logger.debug('Error JSON: ', error_json.content)
#     else:
#         logger.debug('No response data')
