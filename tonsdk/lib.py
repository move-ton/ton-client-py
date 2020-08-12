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
        :param method_name: SDK method name
        :param params: Method params
        :return: Dict
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

        :param string: Any string
        :param fmt: One of 'TYPE_x' constants
        :return: Dict
        """
        if fmt not in [self.TYPE_BASE64, self.TYPE_HEX, self.TYPE_TEXT]:
            raise ValueError(
                "One of 'base64, hex, text' should be provided "
                "for 'fmt' param")
        return {fmt: string}

    def request(self, method: str, params=None, raise_exception=True):
        result = self._request(method, params)

        if raise_exception and not result["success"]:
            raise Exception(result["result"])

        return result["result"]

    def random_generate_bytes(self, length: int) -> str:
        """
        :param length:
        :return: str
        """
        params = {"length": length}
        return self.request(
            method="crypto.random.generateBytes", params=params)

    def derive_sign_keys(self, mnemonic: str) -> Dict:
        """
        :param mnemonic: Mnemonic phrase
        :return: Dict
        """
        params = {"phrase": mnemonic, "wordCount": len(mnemonic.split(" "))}
        return self.request(
            method="crypto.mnemonic.derive.sign.keys", params=params)

    def ton_crc16(self, string: str, string_fmt: str) -> int:
        """
        :param string: String as hex, base64 or plain text
        :param string_fmt: String type ('TonClient.TYPE_x' constants)
        :return: int
        """
        params = self._str_type_dict(string=string, fmt=string_fmt)
        return self.request(method='crypto.ton_crc16', params=params)

    def mnemonic_generate(self, word_count=24) -> str:
        """
        Generate random mnemonic

        :param word_count:
        :return: str
        """
        params = {"wordCount": word_count}
        return self.request(
            method='crypto.mnemonic.from.random', params=params)

    def mnemonic_from_entropy(
            self, entropy: str, entropy_fmt: str, word_count=24) -> str:
        """
        :param entropy: String as hex, base64 or plain text
        :param entropy_fmt: Entropy string type (TonClient.TYPE_x)
        :param word_count:
        :return: str
        """
        params = {
            "wordCount": word_count,
            "entropy": self._str_type_dict(string=entropy, fmt=entropy_fmt)
        }
        return self.request(
            method="crypto.mnemonic.from.entropy", params=params)

    def mnemonic_verify(self, mnemonic: str) -> bool:
        """
        :param mnemonic:
        :return: bool
        """
        params = {"phrase": mnemonic, "wordCount": len(mnemonic.split(" "))}
        return self.request(method='crypto.mnemonic.verify', params=params)

    def mnemonic_words(self) -> str:
        return self.request("crypto.mnemonic.words")

    def sha512(self, string: str, string_fmt: str) -> str:
        """
        :param string: String as hex, base64 or plain text
        :param string_fmt: String type (TonClient.TYPE_x)
        :return: str
        """
        params = {
            "message": self._str_type_dict(string=string, fmt=string_fmt)
        }
        return self.request(method='crypto.sha512', params=params)

    def sha256(self, string: str, string_fmt: str) -> str:
        """
        :param string: String as hex, base64 or plain text
        :param string_fmt: Entropy string type (TonClient.TYPE_x)
        :return: str
        """
        params = {
            "message": self._str_type_dict(string=string, fmt=string_fmt)
        }
        return self.request(method='crypto.sha256', params=params)

    def scrypt(
            self, data: str, n: int, r: int, p: int, dk_len: int, salt: str,
            salt_fmt: str, password: str, password_fmt: str) -> str:
        """
        :param data: Data to encrypt
        :param n: The CPU/Memory cost parameter. Must be larger than 1,
                a power of 2, and less than 2^(128 * r / 8)
        :param r: The parameter specifies block size
        :param p: The parallelization parameter. Is a positive integer
                less than or equal to ((2^32-1) * 32) / (128 * r)
        :param dk_len: The intended output length. Is the length in octets
                of the key to be derived ("keyLength"); it is a positive
                integer less than or equal to (2^32 - 1) * 32.
        :param salt: Salt string
        :param salt_fmt: Salt string type (TonClient.TYPE_x)
        :param password: Password string
        :param password_fmt: Password string type (TonClient.TYPE_x)
        :return: str
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
        :param keypair: Keypair dict {"public": str, "secret": str}
        :return: str
        """
        return self.request(method='crypto.keystore.add', params=keypair)

    def keystore_remove(self, index: str):
        """
        :param index: Keystore index to be removed
        :return:
        """
        self.request(method='crypto.keystore.remove', params=str(index))

    def keystore_clear(self):
        """ Clear keystore """
        self.request(method='crypto.keystore.clear')

    def hdkey_xprv_from_mnemonic(self, mnemonic: str) -> str:
        """
        Get BIP32 key from mnemonic

        :param mnemonic:
        :return: str
        """
        params = {"phrase": mnemonic, "wordCount": len(mnemonic.split(" "))}
        return self.request(
            method='crypto.hdkey.xprv.from.mnemonic', params=params)

    def hdkey_xprv_secret(self, bip32_key: str) -> str:
        """
        Get private key from BIP32 key

        :param bip32_key:
        :return: str
        """
        params = {"serialized": bip32_key}
        return self.request(method='crypto.hdkey.xprv.secret', params=params)

    def hdkey_xprv_public(self, bip32_key: str) -> str:
        """
        Get public key from BIP32 key

        :param bip32_key:
        :return: str
        """
        params = {"serialized": bip32_key}
        return self.request(method='crypto.hdkey.xprv.public', params=params)

    def hdkey_xprv_derive_path(self, bip32_key: str, derive_path: str) -> str:
        """
        :param bip32_key:
        :param derive_path:
        :return: str
        """
        params = {"serialized": bip32_key, 'path': derive_path}
        return self.request(
            method='crypto.hdkey.xprv.derive.path', params=params)

    def hdkey_xprv_derive(self, bip32_key: str, index: int) -> str:
        """
        :param bip32_key:
        :param index:
        :return: str
        """
        params = {"serialized": bip32_key, 'index': index}
        return self.request(method='crypto.hdkey.xprv.derive', params=params)

    def factorize(self, number: str) -> Dict:
        """
        :param number:
        :return: Dict
        """
        return self.request(method='crypto.math.factorize', params=number)

    def ton_public_key_string(self, public_key: str) -> str:
        """
        :param public_key:
        :return: str
        """
        return self.request(
            method='crypto.ton_public_key_string', params=public_key)

    def ed25519_keypair(self) -> Dict:
        """ Generate ed25519 keypair """
        return self.request(method='crypto.ed25519.keypair')

    def modular_power(self, base: str, exponent: str, modulus: str) -> str:
        """
        :param base:
        :param exponent:
        :param modulus:
        :return: str
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

        :param secret_key:
        :return: Dict
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
        :param nonce:
        :param their_public:
        :param secret_key:
        :param message:
        :param message_fmt:
        :param output_fmt:
        :return: str
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
        :param nonce:
        :param their_public:
        :param secret_key:
        :param message:
        :param message_fmt:
        :param output_fmt:
        :return: str
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
        :param key:
        :param message:
        :param message_fmt:
        :param output_fmt:
        :return: str
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
        :param key:
        :param message:
        :param message_fmt:
        :param output_fmt:
        :return: str
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
        :param key:
        :param message:
        :param message_fmt:
        :param output_fmt:
        :return: str
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
        :param nonce:
        :param their_public:
        :param message:
        :param message_fmt:
        :param output_fmt:
        :return: str
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
        :param nonce:
        :param their_public:
        :param secret_key:
        :param message:
        :param message_fmt:
        :param output_fmt:
        :return: str
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

    def query(
            self, table: str, filter: Dict, result: str, order: Dict = None,
            limit: int = None) -> any:
        """
        :param table:
        :param filter: {"field_name": {"rule": "condition"}}
        :param result:
        :param order: {"path": str (field name), "direction": str (ASC|DESC)}
        :param limit:
        :return:
        """
        params = {
            "table": table,
            "filter": json.dumps(filter),
            "result": result,
            "order": order,
            "limit": limit
        }
        result = self.request(method="queries.query", params=params)

        return result["result"]

    def query_wait_for(
            self, table: str, filter: Dict, result: str, order: Dict = None,
            limit: int = None, timeout: int = None) -> any:
        """
        :param table:
        :param filter:
        :param result:
        :param order:
        :param limit:
        :param timeout:
        :return:
        """
        params = {
            "table": table,
            "filter": json.dumps(filter),
            "result": result,
            "order": order,
            "limit": limit,
            "timeout": timeout
        }
        result = self.request(method="queries.wait.for", params=params)

        return result["result"]

    def query_subscribe(
            self, table: str, filter: Dict, result: str) -> int:
        """
        :param table:
        :param filter:
        :param result:
        :return: Handle index
        """
        params = {
            "table": table,
            "filter": json.dumps(filter),
            "result": result
        }
        result = self.request(method="queries.subscribe", params=params)

        return result["handle"]

    def query_get_next(self, handle: int) -> any:
        """
        :param handle:
        :return:
        """
        params = {"handle": handle}
        result = self.request(method="queries.get.next", params=params)

        return result["result"]

    def query_unsubscribe(self, handle: int) -> None:
        """
        :param handle:
        :return:
        """
        params = {"handle": handle}
        return self.request(method="queries.unsubscribe", params=params)

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
