import ctypes
import os
import json
import logging
import platform
import base64

from tonsdk.ton_types import InteropString, InteropJsonResponse

logger = logging.getLogger('ton')

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
LIB_VERSION = '0.25.0'
LIB_DIR = os.path.join(BASE_DIR, 'bin')
LIB_FILENAME = f'ton-rust-client-{LIB_VERSION}'

DEVNET_BASE_URL = 'net.ton.dev'
MAINNET_BASE_URL = 'main.ton.dev'
TON_CLIENT_DEFAULT_SETUP = {
    'baseUrl': DEVNET_BASE_URL,
    'messageRetriesCount': 1,
    'messageExpirationTimeout': 50000,
    'messageExpirationTimeoutGrowFactor': 1.5,
    'messageProcessingTimeout': 50000,
    'messageProcessingTimeoutGrowFactor': 1.5,
    'waitForTimeout': 30000,
    'accessKey': ''
}


def get_lib_basename():
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


class TonClient(object):
    TYPE_TEXT = "text"
    TYPE_HEX = "hex"
    TYPE_BASE64 = "base64"
    lib = None

    def __init__(self, lib_path: str = get_lib_basename()):
        logger.debug('Start new Session')
        self.lib = ctypes.cdll.LoadLibrary(lib_path)

        self.context = self._create_context()

    def setup(self, settings=TON_CLIENT_DEFAULT_SETUP):
        return self._request("setup", settings)

    def version(self):
        return self._request("version", {})

    def _create_context(self):
        """ Create client context """
        context = self.lib.tc_create_context()
        return ctypes.c_uint32(context)

    def _destroy_context(self, context):
        """ Destroy client context """
        self.lib.tc_destroy_context(context)

    def _request(self, method_name, params=None) -> dict:
        """
        Args:
            method_name (str): SDK method name
            params (any): Method params
        Returns:
            dict
        """
        logger.debug('Create request')
        logger.debug(f'Context: {self.context}')

        logger.debug(f'Fn name: {method_name}')
        method_name = InteropString.from_string(method_name)

        logger.debug(f'Data: {params}')
        params = json.dumps(params or {})
        params = InteropString.from_string(params)

        self.lib.tc_json_request.restype = ctypes.POINTER(InteropJsonResponse)
        response = self.lib.tc_json_request(
            self.context, method_name, params)
        logger.debug(f'Response ptr: {response}')

        self.lib.tc_read_json_response.restype = InteropJsonResponse
        read = self.lib.tc_read_json_response(response)
        is_success = read.is_success
        response_json = read.json

        logger.debug(f'Read response: : {read}')
        logger.debug(f'Is success: {is_success}')

        self.lib.tc_destroy_json_response(response)

        return {'success': is_success, 'result': response_json}

    def _guess_str(self, string: str, hex_strict=False) -> str:
        """
        Guess what type string is (text, hex, base64)
        Args:
            string (str): Any string
            hex_strict (bool): If true bytes from hex will be checked
        Returns:
            str
        """
        # Check if string is hex
        try:
            int(string, 16) if not hex_strict else bytes.fromhex(string)
            return self.TYPE_HEX
        except Exception as e:
            logger.debug(e.__str__())

        # Check if string is base64
        try:
            base64.b64decode(string)
            return self.TYPE_BASE64
        except Exception as e:
            logger.debug(e.__str__())

        return self.TYPE_TEXT

    def _guessed_str_dict(self, string: str) -> dict:
        """ Generates dict for API params, based on guessed string type """
        guessed_type = self._guess_str(string)
        if guessed_type == self.TYPE_BASE64:
            message = {"base64": string}
        elif guessed_type == self.TYPE_HEX:
            message = {"hex": string}
        else:
            message = {"text": string}
        logger.debug(f"Guess message type: {message}")

        return message

    def request(self, method: str, params=None, raise_exception=True,
                **kwargs) -> any:
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
        return self.request("crypto.random.generateBytes", params)

    def derive_sign_keys(self, mnemonic: str) -> dict:
        """
        Args:
            mnemonic (str): Mnemonic phrase
        Returns:
            dict
        """
        params = {"phrase": mnemonic, "wordCount": len(mnemonic.split(" "))}
        return self.request("crypto.mnemonic.derive.sign.keys", params)

    def ton_crc16(self, string: str) -> int:
        """
        Args:
            string (str): String as hex, base64 or plain text
        Returns:
            int
        """
        params = self._guessed_str_dict(string)
        return self.request('crypto.ton_crc16', params)

    def mnemonic_generate(self, word_count=24) -> str:
        """
        Generate random mnemonic
        Args:
            word_count (int):
        Returns:
            str
        """
        params = {"wordCount": word_count}
        return self.request('crypto.mnemonic.from.random', params)

    def mnemonic_from_entropy(self, entropy: str, word_count=24) -> str:
        """
        Args:
            entropy (str): String as hex, base64 or plain text
            word_count (int):
        Returns:
            str
        """
        params = {
            "wordCount": word_count,
            "entropy": self._guessed_str_dict(entropy)
        }
        return self.request("crypto.mnemonic.from.entropy", params)

    def mnemonic_verify(self, mnemonic) -> bool:
        """
        Args:
            mnemonic (str):
        Returns:
            bool
        """
        params = {"phrase": mnemonic, "wordCount": len(mnemonic.split(" "))}
        return self.request('crypto.mnemonic.verify', params)

    def mnemonic_words(self) -> str:
        """ Get word list """
        return self.request("crypto.mnemonic.words")

    def sha512(self, string: str) -> str:
        """
        Args:
            string (str): String as hex, base64 or plain text
        Returns:
            str
        """
        params = {"message": self._guessed_str_dict(string)}
        return self.request('crypto.sha512', params)

    def sha256(self, string: str) -> str:
        """
        Args:
            string (str): String as hex, base64 or plain text
        Returns:
            str
        """
        params = {"message": self._guessed_str_dict(string)}
        return self.request('crypto.sha256', params)

    # def scrypt(self, data, log_n, r, p, dk_len, salt=None, hex_salt=None,
    #            base64_salt=None, password=None, hex_password=None,
    #            base64_password=None):
    #     # TODO: не работает
    #     if password:
    #         password = {"text": password}
    #     elif hex_password:
    #         password = {"hex": hex_password}
    #     elif base64_password:
    #         password = {"base64": base64_password}
    #     if salt:
    #         salt = {"text": salt}
    #     elif hex_salt:
    #         salt = {"hex": hex_salt}
    #     elif base64_salt:
    #         salt = {"base64": base64_salt}
    #     return self._request(
    #         'crypto.scrypt', {"data": data, "password": password,
    #         "salt": salt, "logN": log_n, "r": r, "p": p, "dkLen": dk_len})

    def keystore_add(self, keypair: dict) -> str:
        """
        Args:
            keypair (dict): Keypair dict {"public": str, "secret": str}
        Returns:
            str: index in store
        """
        return self.request('crypto.keystore.add', keypair)

    def keystore_remove(self, index) -> None:
        """
        Args:
            index (str, int): Keystore index to be removed
        Returns:
            None or exception
        """
        self.request('crypto.keystore.remove', str(index))

    def keystore_clear(self) -> None:
        """ Clear keystore or exception """
        self.request('crypto.keystore.clear')

    def hdkey_xprv_from_mnemonic(self, mnemonic: str) -> str:
        """
        Get BIP32 key from mnemonic
        Args:
            mnemonic (str):
        Returns:
            str
        """
        params = {"phrase": mnemonic, "wordCount": len(mnemonic.split(" "))}
        return self.request('crypto.hdkey.xprv.from.mnemonic', params)

    def hdkey_xprv_secret(self, bip32_key: str) -> str:
        """
        Get private key from BIP32 key
        Args:
            bip32_key (str):
        Returns:
            str
        """
        params = {"serialized": bip32_key}
        return self.request('crypto.hdkey.xprv.secret', params)

    def hdkey_xprv_public(self, bip32_key: str) -> str:
        """
        Get public key from BIP32 key
        Args:
            bip32_key (str):
        Returns:
            str
        """
        params = {"serialized": bip32_key}
        return self.request('crypto.hdkey.xprv.public', params)

    def hdkey_xprv_derive_path(self, bip32_key: str, derive_path: str) -> str:
        """
        Args:
            bip32_key (str):
            derive_path (str):
        Returns:
            str
        """
        params = {"serialized": bip32_key, 'path': derive_path}
        return self.request('crypto.hdkey.xprv.derive.path', params)

    def hdkey_xprv_derive(self, bip32_key: str, index: int) -> str:
        """
        Args:
            bip32_key (str):
            index (int):
        Returns:
            str
        """
        params = {"serialized": bip32_key, 'index': index}
        return self.request('crypto.hdkey.xprv.derive', params)

    def factorize(self, number: str) -> dict:
        """
        Args:
            number (str):
        Returns:
            dict
        """
        return self.request('crypto.math.factorize', number)

    def ton_public_key_string(self, public_key: str) -> str:
        """
        Args:
            public_key (str):
        Returns:
            str
        """
        return self.request('crypto.ton_public_key_string', public_key)

    def ed25519_keypair(self) -> dict:
        """ Generate ed25519 keypair """
        return self.request('crypto.ed25519.keypair')

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
        return self.request('crypto.math.modularPower', params)

    def nacl_box_keypair(self) -> dict:
        """ Generate nacl box keypair """
        return self.request('crypto.nacl.box.keypair')

    def nacl_sign_keypair(self) -> dict:
        """ Generate nacl sign keypair """
        return self.request('crypto.nacl.sign.keypair')

    def nacl_sign_keypair_from_secret_key(self, secret_key: str) -> dict:
        """
        Generate nack sign keypair from secret key
        Args:
            secret_key (str):
        Returns:
            dict
        """
        return self.request(
            'crypto.nacl.sign.keypair.fromSecretKey', secret_key)

    def nacl_box(self, nonce: str, their_public_key: str, message: str) -> str:
        """
        Args:
            nonce (str):
            their_public_key (str):
            message (str): Message as hex, base64 or plain text
        Returns:
            str
        """
        params = {
            "nonce": nonce,
            "theirPublicKey": their_public_key,
            "message": self._guessed_str_dict(message)
        }
        return self.request("crypto.nacl.box", params)

    def nacl_sign(self, key: str, message: str) -> str:
        """
        Args:
            key (str):
            message (str): Message as hex, base64 or plain text
        Returns:
            str
        """
        params = {
            "key": key,
            "message": self._guessed_str_dict(message)
        }
        return self.request('crypto.nacl.sign', params)

    def nacl_box_keypair_from_secret_key(self, key: str) -> dict:
        return self.request('crypto.nacl.box.keypair.fromSecretKey', key)

    def nacl_secret_box_open(self, nonce: str, their_public_key: str,
                             message: str) -> str:
        """
        Args:
            nonce (str):
            their_public_key (str):
            message (str): Message as hex, base64 or plain text
        Returns:
            str
        """
        params = {
            "nonce": nonce,
            "key": their_public_key,
            "message": self._guessed_str_dict(message)
        }
        return self.request("crypto.nacl.secret.box.open", params)

    def nacl_sign_detached(self, key: str, message: str) -> str:
        """
        Args:
            key (str):
            message (str): Message as hex, base64 or plain text
        Returns:
            str
        """
        params = {
            "key": key,
            "message": self._guessed_str_dict(message)
        }
        return self.request("crypto.nacl.sign.detached", params)

    def nacl_secret_box(self, nonce: str, their_public_key: str, message: str)\
            -> str:
        """
        Args:
            nonce (str):
            their_public_key (str):
            message (str): Message as hex, base64 or plain text
        Returns:
            str
        """
        params = {
            "nonce": nonce,
            "key": their_public_key,
            "message": self._guessed_str_dict(message)
        }
        return self.request("crypto.nacl.secret.box", params)

    def nacl_box_open(self, nonce: str, their_public_key: str, secret_key: str,
                      message: str) -> str:
        """
        Args:
            nonce (str):
            their_public_key (str):
            secret_key (str):
            message (str): Message as hex, base64 or plain text
        Returns:
            str
        """
        params = {
            "nonce": nonce,
            "theirPublicKey": their_public_key,
            "secretKey": secret_key,
            "message": self._guessed_str_dict(message)
        }
        return self.request("crypto.nacl.box.open", params)

    def nacl_sign_open(self, key: str, message: str) -> str:
        """
        Args:
            key (str):
            message (str): Message as hex, base64 or plain text
        Returns:
            str
        """
        params = {
            "key": key,
            "message": self._guessed_str_dict(message)
        }
        return self.request("crypto.nacl.sign.open", params)

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
    #     response = self.lib.tc_json_request_async(
    #         self.context, method_interop, params_interop,
    #         ctypes.c_int32(req_id), on_result)
    #     logger.debug(f'Response: {response}')
    #
    #     self.lib.tc_destroy_json_response(response)
    #     return response
