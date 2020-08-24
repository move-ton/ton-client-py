from typing import Dict, Union, Awaitable

from tonclient.module import TonModule
from tonclient.types import KeyPair, NACL_OUTPUT_HEX


class TonCrypto(TonModule):
    """ Free TON crypto SDK API implementation """
    def random_generate_bytes(self, length: int) -> Union[str, Awaitable]:
        """
        :param length:
        :return: Random bytes of provided length as hex str
        """
        return self.request(
            method="crypto.random.generateBytes", length=length)

    def mnemonic_derive_sign_keys(
            self, mnemonic: str) -> Union[KeyPair, Awaitable]:
        """
        :param mnemonic: Mnemonic phrase
        :return: KeyPair object
        """
        def __result_cb(data: Dict) -> KeyPair:
            return KeyPair(**data)

        return self.request(
            method="crypto.mnemonic.derive.sign.keys", phrase=mnemonic,
            wordCount=len(mnemonic.split(" ")), result_cb=__result_cb)

    def mnemonic_from_random(
            self, word_count: int = 24) -> Union[str, Awaitable]:
        """
        Generate random mnemonic.
        :param word_count:
        :return: Mnemonic phrase
        """
        return self.request(
            method="crypto.mnemonic.from.random", wordCount=word_count)

    def mnemonic_from_entropy(
                self, entropy_fmt: Dict[str, str], word_count: int = 24
            ) -> Union[str, Awaitable]:
        """
        :param entropy_fmt: FmtString prepared dict
        :param word_count:
        :return: Mnemonic from provided entropy
        """
        return self.request(
            method="crypto.mnemonic.from.entropy", wordCount=word_count,
            entropy=entropy_fmt)

    def mnemonic_verify(self, mnemonic: str) -> Union[bool, Awaitable]:
        """
        :param mnemonic:
        :return: Is mnemonic phrase valid or not
        """
        return self.request(
            method="crypto.mnemonic.verify", phrase=mnemonic,
            wordCount=len(mnemonic.split(" ")))

    def mnemonic_words(self) -> Union[str, Awaitable]:
        """
        :return: BIP39 wordlist as string
        """
        return self.request(method="crypto.mnemonic.words")

    def ton_crc16(self, string_fmt: Dict[str, str]) -> Union[int, Awaitable]:
        """
        :param string_fmt: FmtString prepared dict
        :return:
        """
        return self.request(method="crypto.ton_crc16", **string_fmt)

    def sha512(self, string_fmt: Dict[str, str]) -> Union[str, Awaitable]:
        """
        :param string_fmt: FmtString prepared dict
        :return:
        """
        return self.request(method="crypto.sha512", message=string_fmt)

    def sha256(self, string_fmt: Dict[str, str]) -> Union[str, Awaitable]:
        """
        :param string_fmt: FmtString prepared dict
        :return:
        """
        return self.request(method="crypto.sha256", message=string_fmt)

    def scrypt(
                self, data: str, n: int, r: int, p: int, dk_len: int,
                salt_fmt: Dict[str, str], password_fmt: Dict[str, str]
            ) -> Union[str, Awaitable]:
        """
        More info about scrypt: https://tools.ietf.org/html/rfc7914
        :param data: Data to encrypt
        :param n: The CPU/Memory cost parameter. Must be larger than 1,
                a power of 2, and less than 2^(128 * r / 8)
        :param r: The parameter specifies block size
        :param p: The parallelization parameter. Is a positive integer
                less than or equal to ((2^32-1) * 32) / (128 * r)
        :param dk_len: The intended output length. Is the length in octets
                of the key to be derived ("keyLength"); it is a positive
                integer less than or equal to (2^32 - 1) * 32.
        :param salt_fmt: FmtString prepared dict
        :param password_fmt: FmtString prepared dict
        :return:
        """
        return self.request(
            method="crypto.scrypt", data=data, salt=salt_fmt,
            password=password_fmt, logN=n, r=r, p=p, dkLen=dk_len)

    def hdkey_xprv_from_mnemonic(self, mnemonic: str) -> Union[str, Awaitable]:
        """
        Get BIP32 key from mnemonic
        :param mnemonic:
        :return:
        """
        return self.request(
            method="crypto.hdkey.xprv.from.mnemonic", phrase=mnemonic,
            wordCount=len(mnemonic.split(" ")))

    def hdkey_xprv_secret(self, bip32_key: str) -> Union[str, Awaitable]:
        """
        Get private key from BIP32 key
        :param bip32_key:
        :return:
        """
        return self.request(
            method="crypto.hdkey.xprv.secret", serialized=bip32_key)

    def hdkey_xprv_public(self, bip32_key: str) -> Union[str, Awaitable]:
        """
        Get public key from BIP32 key
        :param bip32_key:
        :return:
        """
        return self.request(
            method="crypto.hdkey.xprv.public", serialized=bip32_key)

    def hdkey_xprv_derive_path(
            self, bip32_key: str, derive_path: str) -> Union[str, Awaitable]:
        """
        :param bip32_key:
        :param derive_path:
        :return:
        """
        return self.request(
            method="crypto.hdkey.xprv.derive.path", serialized=bip32_key,
            path=derive_path)

    def hdkey_xprv_derive(
            self, bip32_key: str, index: int) -> Union[str, Awaitable]:
        """
        :param bip32_key:
        :param index:
        :return:
        """
        return self.request(
            method="crypto.hdkey.xprv.derive", serialized=bip32_key,
            index=index)

    def factorize(self, number: str) -> Union[Dict[str, str], Awaitable]:
        """
        :param number:
        :return:
        """
        return self.request("crypto.math.factorize", number)

    def ton_public_key_string(self, public_key: str) -> Union[str, Awaitable]:
        """
        :param public_key:
        :return:
        """
        return self.request("crypto.ton_public_key_string", public_key)

    def ed25519_keypair(self) -> Union[KeyPair, Awaitable]:
        """ Generate ed25519 keypair """
        def __result_cb(data: Dict) -> KeyPair:
            return KeyPair(**data)

        return self.request(
            method="crypto.ed25519.keypair", result_cb=__result_cb)

    def math_modular_power(
                self, base: int, exponent: int, modulus: int
            ) -> Union[str, Awaitable]:
        """
        :param base:
        :param exponent:
        :param modulus:
        :return:
        """
        if modulus == 0:
            raise ValueError(f"'modulus' should be greater than 0")

        return self.request(
            method="crypto.math.modularPower", base=str(base),
            exponent=str(exponent), modulus=str(modulus))

    def nacl_box_keypair(self) -> Union[KeyPair, Awaitable]:
        """ Generate nacl box keypair """
        def __result_cb(data: Dict) -> KeyPair:
            return KeyPair(**data)

        return self.request(
            method="crypto.nacl.box.keypair", result_cb=__result_cb)

    def nacl_box_keypair_from_secret_key(
            self, secret_key: str) -> Union[KeyPair, Awaitable]:
        """
        Generate nacl box keypair from secret key
        :param secret_key:
        :return:
        """
        def __result_cb(data: Dict) -> KeyPair:
            return KeyPair(**data)

        return self.request(
            "crypto.nacl.box.keypair.fromSecretKey", secret_key,
            result_cb=__result_cb)

    def nacl_sign_keypair(self) -> Union[KeyPair, Awaitable]:
        """ Generate nacl sign keypair """
        def __result_cb(data: Dict) -> KeyPair:
            return KeyPair(**data)

        return self.request(
            method="crypto.nacl.sign.keypair", result_cb=__result_cb)

    def nacl_sign_keypair_from_secret_key(
            self, secret_key: str) -> Union[KeyPair, Awaitable]:
        """
        Generate nacl sign keypair from secret key
        :param secret_key:
        :return:
        """
        def __result_cb(data: Dict) -> KeyPair:
            return KeyPair(**data)

        return self.request(
            "crypto.nacl.sign.keypair.fromSecretKey", secret_key,
            result_cb=__result_cb)

    def nacl_box(
                self, nonce: str, their_public: str, secret: str,
                message_fmt: Dict[str, str], output_fmt: str = NACL_OUTPUT_HEX
            ) -> Union[str, Awaitable]:
        """
        :param nonce:
        :param their_public:
        :param secret:
        :param message_fmt:
        :param output_fmt:
        :return:
        """
        return self.request(
            method="crypto.nacl.box", nonce=nonce, theirPublicKey=their_public,
            secretKey=secret, message=message_fmt, outputEncoding=output_fmt)

    def nacl_box_open(
                self, nonce: str, their_public: str, secret: str,
                message_fmt: Dict[str, str], output_fmt: str = NACL_OUTPUT_HEX
            ) -> Union[str, Awaitable]:
        """
        :param nonce:
        :param their_public:
        :param secret:
        :param message_fmt:
        :param output_fmt:
        :return:
        """
        return self.request(
            method="crypto.nacl.box.open", nonce=nonce,
            theirPublicKey=their_public, secretKey=secret, message=message_fmt,
            outputEncoding=output_fmt)

    def nacl_sign(
            self, secret: str, message_fmt: Dict[str, str],
            output_fmt: str = NACL_OUTPUT_HEX) -> Union[str, Awaitable]:
        """
        :param secret:
        :param message_fmt:
        :param output_fmt:
        :return:
        """
        return self.request(
            method="crypto.nacl.sign", key=secret, message=message_fmt,
            outputEncoding=output_fmt)

    def nacl_sign_open(
            self, public: str, message_fmt: Dict[str, str],
            output_fmt: str = NACL_OUTPUT_HEX) -> Union[str, Awaitable]:
        """
        :param public:
        :param message_fmt:
        :param output_fmt:
        :return:
        """
        return self.request(
            method="crypto.nacl.sign.open", key=public, message=message_fmt,
            outputEncoding=output_fmt)

    def nacl_sign_detached(
            self, secret: str, message_fmt: Dict[str, str],
            output_fmt: str = NACL_OUTPUT_HEX) -> Union[str, Awaitable]:
        """
        :param secret:
        :param message_fmt:
        :param output_fmt:
        :return:
        """
        return self.request(
            method="crypto.nacl.sign.detached", key=secret,
            message=message_fmt, outputEncoding=output_fmt)

    def nacl_secret_box(
            self, nonce: str, key: str, message_fmt: Dict[str, str],
            output_fmt: str = NACL_OUTPUT_HEX) -> Union[str, Awaitable]:
        """
        :param nonce:
        :param key:
        :param message_fmt:
        :param output_fmt:
        :return:
        """
        return self.request(
            method="crypto.nacl.secret.box", nonce=nonce, key=key,
            message=message_fmt, outputEncoding=output_fmt)

    def nacl_secret_box_open(
            self, nonce: str, key: str, message_fmt: Dict[str, str],
            output_fmt: str = NACL_OUTPUT_HEX) -> Union[str, Awaitable]:
        """
        :param nonce:
        :param key:
        :param message_fmt:
        :param output_fmt:
        :return:
        """
        return self.request(
            method="crypto.nacl.secret.box.open", nonce=nonce, key=key,
            message=message_fmt, outputEncoding=output_fmt)
