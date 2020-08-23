from typing import Dict

from tonclient.module import TonModule
from tonclient.types import KeyPair, NACL_OUTPUT_HEX


class TonCrypto(TonModule):
    """ Free TON crypto SDK API implementation """
    def random_generate_bytes(self, length: int) -> str:
        """
        :param length:
        :return: Random bytes of provided length as hex str
        """
        return self.request(
            method="crypto.random.generateBytes", length=length)

    def mnemonic_derive_sign_keys(self, mnemonic: str) -> KeyPair:
        """
        :param mnemonic: Mnemonic phrase
        :return: KeyPair object
        """
        response = self.request(
            method="crypto.mnemonic.derive.sign.keys", phrase=mnemonic,
            wordCount=len(mnemonic.split(" ")))
        return KeyPair(**response)

    def mnemonic_from_random(self, word_count: int = 24) -> str:
        """
        Generate random mnemonic.
        :param word_count:
        :return: Mnemonic phrase
        """
        return self.request(
            method="crypto.mnemonic.from.random", wordCount=word_count)

    def mnemonic_from_entropy(
            self, entropy_fmt: Dict[str, str], word_count: int = 24) -> str:
        """
        :param entropy_fmt: FmtString prepared dict
        :param word_count:
        :return: Mnemonic from provided entropy
        """
        return self.request(
            method="crypto.mnemonic.from.entropy", wordCount=word_count,
            entropy=entropy_fmt)

    def mnemonic_verify(self, mnemonic: str) -> bool:
        """
        :param mnemonic:
        :return: Is mnemonic phrase valid or not
        """
        return self.request(
            method="crypto.mnemonic.verify", phrase=mnemonic,
            wordCount=len(mnemonic.split(" ")))

    def mnemonic_words(self) -> str:
        """
        :return: BIP39 wordlist as string
        """
        return self.request(method="crypto.mnemonic.words")

    def ton_crc16(self, string_fmt: Dict[str, str]) -> int:
        """
        :param string_fmt: FmtString prepared dict
        :return:
        """
        return self.request(method="crypto.ton_crc16", **string_fmt)

    def sha512(self, string_fmt: Dict[str, str]) -> str:
        """
        :param string_fmt: FmtString prepared dict
        :return:
        """
        return self.request(method="crypto.sha512", message=string_fmt)

    def sha256(self, string_fmt: Dict[str, str]) -> str:
        """
        :param string_fmt: FmtString prepared dict
        :return:
        """
        return self.request(method="crypto.sha256", message=string_fmt)

    def scrypt(
            self, data: str, n: int, r: int, p: int, dk_len: int,
            salt_fmt: Dict[str, str], password_fmt: Dict[str, str]) -> str:
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

    def hdkey_xprv_from_mnemonic(self, mnemonic: str) -> str:
        """
        Get BIP32 key from mnemonic
        :param mnemonic:
        :return:
        """
        return self.request(
            method="crypto.hdkey.xprv.from.mnemonic", phrase=mnemonic,
            wordCount=len(mnemonic.split(" ")))

    def hdkey_xprv_secret(self, bip32_key: str) -> str:
        """
        Get private key from BIP32 key
        :param bip32_key:
        :return:
        """
        return self.request(
            method="crypto.hdkey.xprv.secret", serialized=bip32_key)

    def hdkey_xprv_public(self, bip32_key: str) -> str:
        """
        Get public key from BIP32 key
        :param bip32_key:
        :return:
        """
        return self.request(
            method="crypto.hdkey.xprv.public", serialized=bip32_key)

    def hdkey_xprv_derive_path(self, bip32_key: str, derive_path: str) -> str:
        """
        :param bip32_key:
        :param derive_path:
        :return:
        """
        return self.request(
            method="crypto.hdkey.xprv.derive.path", serialized=bip32_key,
            path=derive_path)

    def hdkey_xprv_derive(self, bip32_key: str, index: int) -> str:
        """
        :param bip32_key:
        :param index:
        :return:
        """
        return self.request(
            method="crypto.hdkey.xprv.derive", serialized=bip32_key,
            index=index)

    def factorize(self, number: str) -> Dict[str, str]:
        """
        :param number:
        :return:
        """
        return self.request("crypto.math.factorize", number)

    def ton_public_key_string(self, public_key: str) -> str:
        """
        :param public_key:
        :return:
        """
        return self.request("crypto.ton_public_key_string", public_key)

    def ed25519_keypair(self) -> KeyPair:
        """ Generate ed25519 keypair """
        method = "crypto.ed25519.keypair"

        if self.is_async:
            def __async_result(result: Dict):
                return KeyPair(**result)
            return self.request(method=method, result_cb=__async_result)

        response = self.request(method=method)
        return KeyPair(**response)

    def math_modular_power(
            self, base: int, exponent: int, modulus: int) -> str:
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

    def nacl_box_keypair(self) -> KeyPair:
        """ Generate nacl box keypair """
        response = self.request(method="crypto.nacl.box.keypair")
        return KeyPair(**response)

    def nacl_box_keypair_from_secret_key(self, secret_key: str) -> KeyPair:
        """
        Generate nacl box keypair from secret key
        :param secret_key:
        :return:
        """
        response = self.request(
            "crypto.nacl.box.keypair.fromSecretKey", secret_key)
        return KeyPair(**response)

    def nacl_sign_keypair(self) -> KeyPair:
        """ Generate nacl sign keypair """
        response = self.request(method="crypto.nacl.sign.keypair")
        return KeyPair(**response)

    def nacl_sign_keypair_from_secret_key(self, secret_key: str) -> KeyPair:
        """
        Generate nacl sign keypair from secret key
        :param secret_key:
        :return:
        """
        response = self.request(
            "crypto.nacl.sign.keypair.fromSecretKey", secret_key)
        return KeyPair(**response)

    def nacl_box(
                self, nonce: str, their_public: str, secret: str,
                message_fmt: Dict[str, str], output_fmt: str = NACL_OUTPUT_HEX
            ) -> str:
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
            ) -> str:
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
            output_fmt: str = NACL_OUTPUT_HEX) -> str:
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
            output_fmt: str = NACL_OUTPUT_HEX) -> str:
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
            output_fmt: str = NACL_OUTPUT_HEX) -> str:
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
            output_fmt: str = NACL_OUTPUT_HEX) -> str:
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
            output_fmt: str = NACL_OUTPUT_HEX) -> str:
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
