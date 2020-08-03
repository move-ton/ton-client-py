import ctypes
import os
import json
import logging
import platform
from typing import Dict, Callable
import errors
import default_contracts as contracts
from default_contracts import TonContract
from ton_types import InteropString, ResultCb, InteropJsonResponse

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
        raise RuntimeError(f'No library for current platform "{plt.capitalize()}"')
    return os.path.join(LIB_DIR, f'{LIB_FILENAME}.{lib_ext_dict[plt]}')


def _on_result(
        request_id: int,
        result_json: InteropString,
        error_json: InteropString, flags: int):
    """ Python callback for lib async request """
    logger.debug('Async callback fired')
    logger.debug(
        f'Request ID: {request_id}\n'
        f'Result JSON: {result_json}\n'
        f'Error JSON: {error_json}\n'
        f'Flags: {flags}\n')

    if result_json.len > 0:
        logger.debug('Result JSON: ', result_json.content)
    elif error_json.len > 0:
        logger.debug('Error JSON: ', error_json.content)
    else:
        logger.debug('No response data')


class TonClient(object):
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

    def _request(self, method_name, params: Dict) -> Dict:
        logger.debug('Create request')
        logger.debug(f'Context: {self.context}')

        method = method_name.encode()
        method_interop = InteropString(
            ctypes.cast(
                method,
                ctypes.c_char_p),
            len(method))
        logger.debug(f'Fn name: {method}')

        params = json.dumps(params).encode()
        params_interop = InteropString(
            ctypes.cast(
                params,
                ctypes.c_char_p),
            len(params))
        logger.debug(f'Data: {params}')

        self.lib.tc_json_request.restype = ctypes.POINTER(InteropJsonResponse)
        response = self.lib.tc_json_request(
            self.context, method_interop, params_interop)
        logger.debug(f'Response ptr: {response}')

        self.lib.tc_read_json_response.restype = InteropJsonResponse
        read = self.lib.tc_read_json_response(response)
        is_success = read.is_success
        response_json = read.json

        logger.debug(f'Read response: : {read}')
        logger.debug(f'Is success: {is_success}')

        self.lib.tc_destroy_json_response(response)
        return {
            'success': is_success, 'result': response_json
        }

    def random_generateBytes(self, length):
        return self._request("crypto.random.generateBytes", {"length": length})

    def fromMnemonic_ToKeyPair(self, mnemonic):
        return self._request("crypto.mnemonic.derive.sign.keys", {
                             "phrase": mnemonic, "wordCount": len(mnemonic.split(" "))})

    def generateMnemonic(self, wordCount=24):
        return self._request('crypto.mnemonic.from.random', {
                             "wordCount": wordCount})

    def ton_crc16(self, text=None, hex_text=None, base64_text=None):
        if text:
            data = {"text": text}
        elif hex_text:
            data = {"hex": hex_text}
        elif base64_text:
            data = {"base64": base64_text}
        return self._request('crypto.ton_crc16', data)

    def mnemonic_from_entropy(
            self, text=None, hex_text=None, base64_text=None, wordCount=24):
        data = {}
        if text:
            entropy = {"text": text}
        elif hex_text:
            entropy = {"hex": hex_text}
        elif base64_text:
            entropy = {"base64": base64_text}
        data["wordCount"] = wordCount
        data['entropy'] = entropy
        return self._request("crypto.mnemonic.from.entropy", data)

    def mnemonic_verify(self, mnemonic):
        return self._request('crypto.mnemonic.verify', {
                             "phrase": mnemonic, "wordCount": len(mnemonic.split(" "))})

    def mnemonic_words(self):
        return self._request("crypto.mnemonic.words", {})

    def sha512(self, message=None, hex_message=None, base64_message=None):
        if message:
            message = {"text": message}
        elif hex_message:
            message = {"hex": hex_message}
        elif base64_message:
            message = {"base64": base64_message}
        return self._request('crypto.sha512', {"message": message})

    def sha256(self, message=None, hex_message=None, base64_message=None):
        if message:
            message = {"text": message}
        elif hex_message:
            message = {"hex": hex_message}
        elif base64_message:
            message = {"base64": base64_message}
        return self._request('crypto.sha256', {"message": message})

    def scrypt(self, data, logn, r, p, dk_len, salt=None, hex_salt=None, base64_salt=None,
               password=None, hex_password=None, base64_password=None, ):
        # TODO: не работает
        if password:
            password = {"text": password}
        elif hex_password:
            password = {"hex": hex_password}
        elif base64_password:
            password = {"base64": base64_password}
        if salt:
            salt = {"text": salt}
        elif hex_salt:
            salt = {"hex": hex_salt}
        elif base64_salt:
            salt = {"base64": base64_salt}
        return self._request(
            'crypto.scrypt', {"data": data, "password": password, "salt": salt, "logN": logn, "r": r, "p": p, "dkLen": dk_len})

    def keystore_add(self, keypair):
        return self._request('crypto.keystore.add', keypair)

    def keystore_remove(self, index):
        return self._request('crypto.keystore.remove', str(index))

    def keystore_clear(self):
        return self._request('crypto.keystore.clear', {})

    def hdkey_xprv_secret(self, bip32_key):
        # serialized = bip32 key
        ''' Возвращяет приватный ключ из bip32 ключа'''
        return self._request('crypto.hdkey.xprv.secret',
                             {"serialized": bip32_key})

    def hdkey_xprv_public(self, bip32_key):
        # serialized = bip32 key
        ''' Возвращяет публичный ключ из bip32 ключа'''
        return self._request('crypto.hdkey.xprv.public',
                             {"serialized": bip32_key})

    def hdkey_xprv_from_mnemonic(self, mnemonic):
        # serialized = bip32 key
        ''' Возвращяет bip32 ключ'''
        return self._request('crypto.hdkey.xprv.from.mnemonic',
                             {"phrase": mnemonic, "wordCount": len(mnemonic.split(" "))})

    def hdkey_xprv_derive_path(self, bip32_key, derive_path):
        return self._request('crypto.hdkey.xprv.derive.path', {
                             "serialized": bip32_key, 'path': derive_path})

    def hdkey_xprv_derive(self, bip32_key, index):
        return self._request('crypto.hdkey.xprv.derive', {
                             "serialized": bip32_key, 'index': index})

    def factorize(self, number):
        return self._request('crypto.math.factorize', number)

    def ton_public_key_string(self, public_key):
        return self._request('crypto.ton_public_key_string', public_key)

    def nacl_box_keypair(self):
        return self._request('crypto.nacl.box.keypair', {})

    def ed25519_keypair(self):
        return self._request('crypto.ed25519.keypair', {})

    def modularPower(self, base, exponent, modulus):
        return self._request('crypto.math.modularPower', {
                             'base': base, 'exponent': exponent, 'modulus': modulus})

    def nacl_sign_keypair(self):
        return self._request('crypto.nacl.sign.keypair', {})

    def nacl_sign_keypair_from_secret_key(self, secret_key):
        return self._request(
            'crypto.nacl.sign.keypair.fromSecretKey', secret_key)

    def nacl_box(self, nonce, their_public_key, message=None,
                 hex_message=None, base64_message=None, ):
        if message:
            message = {"text": message}
        elif hex_message:
            message = {"hex": hex_message}
        elif base64_message:
            message = {"base64": base64_message}
        return self._request("crypto.nacl.box", {
                             'message': message, 'nonce': nonce, 'theirPublicKey': their_public_key})

    def nacl_sign(self, key, message=None, hex_message=None,
                  base64_message=None):
        if message:
            message = {"text": message}
        elif hex_message:
            message = {"hex": hex_message}
        elif base64_message:
            message = {"base64": base64_message}
        return self._request('crypto.nacl.sign', {
                             "message": message, "key": key})

    def nacl_box_keypair_from_secret_key(self, secret_key):
        return self._request(
            'crypto.nacl.box.keypair.fromSecretKey', secret_key)

    def nacl_secret_box_open(
            self, nonce, their_public_key, message=None, hex_message=None, base64_message=None):
        if message:
            message = {"text": message}
        elif hex_message:
            message = {"hex": hex_message}
        elif base64_message:
            message = {"base64": base64_message}
        return self._request("crypto.nacl.secret.box.open", {
                             "message": message, "nonce": nonce, "key": their_public_key})

    def nacl_sign_detached(
            self, key, message=None, hex_message=None, base64_message=None):
        if message:
            message = {"text": message}
        elif hex_message:
            message = {"hex": hex_message}
        elif base64_message:
            message = {"base64": base64_message}
        return self._request("crypto.nacl.sign.detached", {
                             "message": message, "key": key})

    def nacl_secret_box(self, nonce, their_public_key, message=None, hex_message=None,
                        base64_message=None):
        if message:
            message = {"text": message}
        elif hex_message:
            message = {"hex": hex_message}
        elif base64_message:
            message = {"base64": base64_message}
        return self._request("crypto.nacl.secret.box", {
                             "message": message, "nonce": nonce, "key": their_public_key})

    def nacl_box_open(
            self, nonce, their_public_key, key, message=None, hex_message=None, base64_message=None):
        if message:
            message = {"text": message}
        elif hex_message:
            message = {"hex": hex_message}
        elif base64_message:
            message = {"base64": base64_message}
        return self._request("crypto.nacl.box.open", {
                             "message": message, "nonce": nonce, "theirPublicKey": their_public_key, "secretKey": key})

    def nacl_sign_open(self, key, message=None, hex_message=None,
                       base64_message=None):
        if message:
            message = {"text": message}
        elif hex_message:
            message = {"hex": hex_message}
        elif base64_message:
            message = {"base64": base64_message}
        return self._request("crypto.nacl.sign.open", {
                             "message": message, "key": key})
    # async def _request_async(self, method_name, params: Dict, req_id: int, cb: Callable = _on_result):
    #     logger.debug('Create request (async)')
    #     logger.debug(f'Context: {self.context}')
    #
    #     method = method_name.encode()
    #     method_interop = InteropString(ctypes.cast(method, ctypes.c_char_p), len(method))
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
    #         self.context, method_interop, params_interop, ctypes.c_int32(req_id), on_result)
    #     logger.debug(f'Response: {response}')
    #
    #     self.lib.tc_destroy_json_response(response)
    #     return response


class TonWallet(object):

    def __init__(self, ton: TonClient, mnemonic=None, private_key=None):
        self.ton = ton
        if mnemonic:
            data = ton._request(
                'crypto.mnemonic.derive.sign.keys', {
                    'phrase': mnemonic})["result"]
            self.secret = data["secret"]
            self.public = data["public"]
            self.mnemonic = mnemonic
        elif private_key:
            data = ton._request(
                "crypto.nacl.sign.keypair.fromSecretKey",
                private_key)["result"]
            self.private = data["secret"]
            self.public = data["public"]
        else:
            mnemonic = ton._request(
                'crypto.mnemonic.from.random', {})["result"]
            data = ton._request(
                'crypto.mnemonic.derive.sign.keys', {
                    'phrase': mnemonic})["result"]
            self.secret = data["secret"]
            self.public = data["public"]
            self.mnemonic = mnemonic

    def deploy_wallet(self, workchainId=0):
        return self.ton._request('contracts.deploy', {
            'abi': contracts.wallet.abi,
            'constructorParams': {},
            'imageBase64': contracts.wallet.tvm,
            'keyPair': self.__dict__(),
            'workchainId': workchainId
        })

    def deploy_contract(self, contract: TonContract, workchainId=0):
        return self.ton._request('contracts.deploy', {
            'abi': contract.abi,
            'constructorParams': {},
            'imageBase64': contract.tvm,
            'keyPair': self.__dict__(),
            'workchainId': workchainId
        })

    def interact_with_contract(
            self, contract, functionName, inputData, workchainId=0):
        deploy_address = self.ton._request("contracts.deploy.address", {
            "abi": contract.abi,
            'imageBase64': contract.tvm,
            "keyPair": self.__dict__()
        })["result"]

        return self.ton._request("contracts.run", {
            "address": deploy_address,
            "abi": contract.abi,
            "functionName": functionName,
            "input": inputData,
            "keyPair": self.__dict__()
        })

    def address(self):
        return self.ton._request("contracts.deploy.address", {
            "abi": contracts.wallet.abi,
            'imageBase64': contracts.wallet.tvm,
            "keyPair": self.__dict__()
        })["result"]

    def send(self, dest, value, bounce=True):
        ''' 1 crystal = 1000000000 '''
        return self.ton._request("contracts.run", {
            "address": self.address(),
            "abi": contracts.wallet.abi,
            "functionName": "sendTransaction",
            "input": {
                "dest": str(dest),
                "value": value,
                "bounce": bounce
            },
            "keyPair": self.__dict__()
        })

    @property
    def keypair(self):
        return dict(public=self.public, secret=self.secret)

    def __str__(self):
        return self.address()
