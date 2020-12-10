import functools
import inspect
from typing import Callable, Any

from tonclient.types import KeyPair


class Response(object):
    @staticmethod
    def __pretty(function, _callback: Callable[[Any], Any] = None):
        """ Base decorator function """
        @functools.wraps(function)
        def response_or_generator(*args, **kwargs):
            def generator_wrapper():
                for item in result:
                    data = item['response_data']
                    if data is not None:
                        item['response_data'] = _callback(data)
                    yield item

            def response_wrapper():
                return _callback(result)

            async def async_response_wrapper():
                _result = await result
                return _callback(_result)

            async def async_generator_wrapper():
                async for item in result:
                    data = item['response_data']
                    if data is not None:
                        item['response_data'] = _callback(data)
                    yield item

            result = function(*args, **kwargs)
            if inspect.isgenerator(result):
                return generator_wrapper()
            elif inspect.iscoroutine(result):
                return async_response_wrapper()
            elif inspect.isasyncgen(result):
                return async_generator_wrapper()
            return response_wrapper()

        return response_or_generator

    @classmethod
    def version(cls, function):
        def __callback(result):
            return result['version']
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def get_api_reference(cls, function):
        def __callback(result):
            return result['api']
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def sha256(cls, function):
        def __callback(result):
            return result['hash']
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def sha512(cls, function):
        def __callback(result):
            return result['hash']
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def hdkey_xprv_from_mnemonic(cls, function):
        def __callback(result):
            return result['xprv']
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def hdkey_secret_from_xprv(cls, function):
        def __callback(result):
            return result['secret']
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def hdkey_public_from_xprv(cls, function):
        def __callback(result):
            return result['public']
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def hdkey_derive_from_xprv(cls, function):
        def __callback(result):
            return result['xprv']
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def hdkey_derive_from_xprv_path(cls, function):
        def __callback(result):
            return result['xprv']
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def convert_public_key_to_ton_safe_format(cls, function):
        def __callback(result):
            return result['ton_public_key']
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def generate_random_sign_keys(cls, function):
        def __callback(result):
            return KeyPair(**result)
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def verify_signature(cls, function):
        def __callback(result):
            return result['unsigned']
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def modular_power(cls, function):
        def __callback(result):
            return result['modular_power']
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def factorize(cls, function):
        def __callback(result):
            return result['factors']
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def ton_crc16(cls, function):
        def __callback(result):
            return result['crc']
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def generate_random_bytes(cls, function):
        def __callback(result):
            return result['bytes']
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def mnemonic_words(cls, function):
        def __callback(result):
            return result['words']
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def mnemonic_from_random(cls, function):
        def __callback(result):
            return result['phrase']
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def mnemonic_from_entropy(cls, function):
        def __callback(result):
            return result['phrase']
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def mnemonic_verify(cls, function):
        def __callback(result):
            return result['valid']
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def mnemonic_derive_sign_keys(cls, function):
        def __callback(result):
            return KeyPair(**result)
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def nacl_sign_keypair_from_secret_key(cls, function):
        def __callback(result):
            return KeyPair(**result)
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def nacl_sign(cls, function):
        def __callback(result):
            return result['signed']
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def nacl_sign_detached(cls, function):
        def __callback(result):
            return result['signature']
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def nacl_sign_open(cls, function):
        def __callback(result):
            return result['unsigned']
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def nacl_box_keypair(cls, function):
        def __callback(result):
            return KeyPair(**result)
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def nacl_box_keypair_from_secret_key(cls, function):
        def __callback(result):
            return KeyPair(**result)
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def nacl_box(cls, function):
        def __callback(result):
            return result['encrypted']
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def nacl_box_open(cls, function):
        def __callback(result):
            return result['decrypted']
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def nacl_secret_box(cls, function):
        def __callback(result):
            return result['encrypted']
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def nacl_secret_box_open(cls, function):
        def __callback(result):
            return result['decrypted']
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def scrypt(cls, function):
        def __callback(result):
            return result['key']
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def chacha20(cls, function):
        def __callback(result):
            return result['data']

        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def get_signing_box(cls, function):
        def __callback(result):
            return result['handle']

        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def signing_box_get_public_key(cls, function):
        def __callback(result):
            return result['pubkey']

        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def signing_box_sign(cls, function):
        def __callback(result):
            return result['signature']

        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def query_collection(cls, function):
        def __callback(result):
            return result['result']
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def wait_for_collection(cls, function):
        def __callback(result):
            return result['result']
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def subscribe_collection(cls, function):
        def __callback(result):
            return result.get('result', result)
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def query(cls, function):
        def __callback(result):
            return result['result']

        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def parse_message(cls, function):
        def __callback(result):
            return result['parsed']
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def parse_transaction(cls, function):
        def __callback(result):
            return result['parsed']
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def parse_account(cls, function):
        def __callback(result):
            return result['parsed']
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def parse_block(cls, function):
        def __callback(result):
            return result['parsed']
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def parse_shardstate(cls, function):
        def __callback(result):
            return result['parsed']

        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def get_boc_hash(cls, function):
        def __callback(result):
            return result['hash']

        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def get_blockchain_config(cls, function):
        def __callback(result):
            return result['config_boc']
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def convert_address(cls, function):
        def __callback(result):
            return result['address']
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def send_message(cls, function):
        def __callback(result):
            return result.get('shard_block_id', result)
        return cls.__pretty(function=function, _callback=__callback)

    @classmethod
    def run_get(cls, function):
        def __callback(result):
            return result['output']
        return cls.__pretty(function=function, _callback=__callback)
