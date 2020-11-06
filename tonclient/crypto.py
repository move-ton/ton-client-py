from typing import Dict, Union, List

from tonclient.decorators import Response
from tonclient.module import TonModule
from tonclient.types import KeyPair, DEFAULT_HDKEY_DERIVATION_PATH


class TonCrypto(TonModule):
    """ Free TON crypto SDK API implementation """
    @Response.sha256
    def sha256(self, data: Union[str, bytes]) -> str:
        """
        Calculates SHA256 hash of the specified data.
        :param data: Base64 encoded data for hash calculation
        :return:
        """
        if type(data) is bytes:
            data = data.decode()
        return self.request(method='crypto.sha256', data=data)

    @Response.sha512
    def sha512(self, data: Union[str, bytes]) -> str:
        """
        Calculates SHA512 hash of the specified data.
        :param data: Base64 encoded data for hash calculation
        :return:
        """
        if type(data) is bytes:
            data = data.decode()
        return self.request(method='crypto.sha512', data=data)

    @Response.hdkey_xprv_from_mnemonic
    def hdkey_xprv_from_mnemonic(self, phrase: str) -> str:
        """
        Generate the extended master private key that will be the root for
        all the derived keys.
        :param phrase: String with seed phrase
        :return:
        """
        return self.request(
            method='crypto.hdkey_xprv_from_mnemonic', phrase=phrase)

    @Response.hdkey_secret_from_xprv
    def hdkey_secret_from_xprv(self, xprv: str) -> str:
        """
        Extracts the private key from the serialized extended private key.
        :param xprv: Serialized extended private key
        :return:
        """
        return self.request(
            method='crypto.hdkey_secret_from_xprv', xprv=xprv)

    @Response.hdkey_public_from_xprv
    def hdkey_public_from_xprv(self, xprv: str) -> str:
        """
        Extracts the public key from the serialized extended private key.
        :param xprv: Serialized extended private key
        :return:
        """
        return self.request(
            method='crypto.hdkey_public_from_xprv', xprv=xprv)

    @Response.hdkey_derive_from_xprv
    def hdkey_derive_from_xprv(
            self, xprv: str, child_index: int, hardened: bool) -> str:
        """
        Returns derived extended private key derived from the specified
        extended private key and child index
        :param xprv: Serialized extended private key
        :param child_index: Child index (see BIP-0032)
        :param hardened: Indicates the derivation of hardened/not-hardened
                key (see BIP-0032)
        :return:
        """
        return self.request(
            method='crypto.hdkey_derive_from_xprv', xprv=xprv,
            child_index=child_index, hardened=hardened)

    @Response.hdkey_derive_from_xprv_path
    def hdkey_derive_from_xprv_path(self, xprv: str, path: str) -> str:
        """
        Derives the extended private key from the specified key and path.
        :param xprv: Serialized extended private key
        :param path: Derivation path, for instance "m/44'/396'/0'/0/0"
        :return:
        """
        return self.request(
            method='crypto.hdkey_derive_from_xprv_path', xprv=xprv,
            path=path)

    @Response.convert_public_key_to_ton_safe_format
    def convert_public_key_to_ton_safe_format(self, public_key: str) -> str:
        """
        Converts public key to ton safe_format.
        :param public_key: Public key
        :return:
        """
        return self.request(
            method='crypto.convert_public_key_to_ton_safe_format',
            public_key=public_key)

    @Response.generate_random_sign_keys
    def generate_random_sign_keys(self) -> KeyPair:
        """
        Generates random ed25519 key pair.
        :return:
        """
        return self.request(method='crypto.generate_random_sign_keys')

    def sign(
            self, unsigned: Union[str, bytes], keys: KeyPair
    ) -> Dict[str, str]:
        """
        Signs a data using the provided keys.
        :param unsigned: Base64 encoded data to be signed
        :param keys: Sign keys
        :return:
        """
        if type(unsigned) is bytes:
            unsigned = unsigned.decode()
        return self.request(
            method='crypto.sign', unsigned=unsigned, keys=keys.dict)

    @Response.verify_signature
    def verify_signature(self, signed: Union[str, bytes], public: str) -> str:
        """
        Verifies signed data using the provided public key.
        :param signed: Base64 encoded signature to be verified
        :param public: Signer's public key hex
        :return: Base64 encoded unsigned data
        """
        if type(signed) is bytes:
            signed = signed.decode()
        return self.request(
            method='crypto.verify_signature', signed=signed,
            public=public)

    @Response.modular_power
    def modular_power(self, base: str, exponent: str, modulus: str) -> str:
        """
        Performs modular exponentiation for big integers
        (`base`^`exponent` mod `modulus`).
        See [https://en.wikipedia.org/wiki/Modular_exponentiation]
        :param base: 'base' argument of calculation
        :param exponent: 'exponent' argument of calculation
        :param modulus: 'modulus' argument of calculation
        :return:
        """
        return self.request(
            method='crypto.modular_power', base=base, exponent=exponent,
            modulus=modulus)

    @Response.factorize
    def factorize(self, composite: str) -> List[str]:
        """
        Performs prime factorization – decomposition of a composite number
        into a product of smaller prime integers (factors).
        See [https://en.wikipedia.org/wiki/Integer_factorization]
        :param composite: Hexadecimal representation of u64 composite number
        :return: Two factors of composite or empty if composite
                can't be factorized
        """
        return self.request(
            method='crypto.factorize', composite=composite)

    @Response.ton_crc16
    def ton_crc16(self, data: Union[str, bytes]) -> int:
        """
        Calculates CRC16 using TON algorithm.
        :param data: Base64 encoded data for CRC calculation
        :return:
        """
        if type(data) is bytes:
            data = data.decode()
        return self.request(method='crypto.ton_crc16', data=data)

    @Response.generate_random_bytes
    def generate_random_bytes(self, length: int) -> str:
        """
        Generates random byte array of the specified length and returns
        it in base64 format
        :param length: Size of random byte array
        :return: Base64 encoded generated bytes
        """
        return self.request(
            method='crypto.generate_random_bytes', length=length)

    @Response.mnemonic_words
    def mnemonic_words(self, dictionary: int = None) -> str:
        """
        Prints the list of words from the specified dictionary.
        :param dictionary: Dictionary identifier
        :return: String of dictionary words
        """
        return self.request(
            method='crypto.mnemonic_words', dictionary=dictionary)

    @Response.mnemonic_from_random
    def mnemonic_from_random(
            self, dictionary: int = None, word_count: int = None) -> str:
        """
        Generates a random mnemonic from the specified dictionary
        and word count.
        :param dictionary: Dictionary identifier
        :param word_count: Mnemonic word count
        :return: String of mnemonic words
        """
        return self.request(
            method='crypto.mnemonic_from_random', dictionary=dictionary,
            word_count=word_count)

    @Response.mnemonic_from_entropy
    def mnemonic_from_entropy(
            self, entropy: str, dictionary: int = None,
            word_count: int = None) -> str:
        """
        Generates mnemonic from pre-generated entropy.
        :param entropy: Hex encoded entropy bytes
        :param dictionary: Dictionary identifier
        :param word_count: Mnemonic word count
        :return: String of mnemonic words
        """
        return self.request(
            method='crypto.mnemonic_from_entropy', entropy=entropy,
            dictionary=dictionary, word_count=word_count)

    @Response.mnemonic_verify
    def mnemonic_verify(
            self, phrase: str, dictionary: int = None,
            word_count: int = None) -> bool:
        """
        The phrase supplied will be checked for word length and validated
        according to the checksum specified in BIP0039.
        :param phrase: Mnemonic phrase
        :param dictionary: Dictionary identifier
        :param word_count: Mnemonic word count
        :return:
        """
        return self.request(
            method='crypto.mnemonic_verify', phrase=phrase,
            dictionary=dictionary, word_count=word_count)

    @Response.mnemonic_derive_sign_keys
    def mnemonic_derive_sign_keys(
            self, phrase: str, path: str = None, dictionary: int = None,
            word_count: int = None) -> KeyPair:
        """
        Validates the seed phrase, generates master key and then derives
        the key pair from the master key and the specified path.
        :param phrase: Mnemonic phrase
        :param path: Derivation path, for instance "m/44'/396'/0'/0/0"
        :param dictionary: Dictionary identifier
        :param word_count: Mnemonic word count
        :return:
        """
        return self.request(
            method='crypto.mnemonic_derive_sign_keys', phrase=phrase,
            path=path, dictionary=dictionary, word_count=word_count)

    @Response.nacl_sign_keypair_from_secret_key
    def nacl_sign_keypair_from_secret_key(self, secret: str) -> KeyPair:
        """
        Generates a key pair for signing from the secret key.
        :param secret: Secret key
        :return:
        """
        return self.request(
            method='crypto.nacl_sign_keypair_from_secret_key',
            secret=secret)

    @Response.nacl_sign
    def nacl_sign(self, unsigned: Union[str, bytes], secret: str) -> str:
        """
        Signs data using the signer's secret key.
        :param unsigned: Base64 encoded data to be signed
        :param secret: Signer's secret key
        :return: Base64 encoded signed data
        """
        if type(unsigned) is bytes:
            unsigned = unsigned.decode()
        return self.request(
            method='crypto.nacl_sign', unsigned=unsigned, secret=secret)

    @Response.nacl_sign_detached
    def nacl_sign_detached(
            self, unsigned: Union[str, bytes], secret: str) -> str:
        """
        :param unsigned: Base64 encoded data to be signed
        :param secret: Signer's secret key
        :return: Hex encoded sign
        """
        if type(unsigned) is bytes:
            unsigned = unsigned.decode()
        return self.request(
            method='crypto.nacl_sign_detached', unsigned=unsigned,
            secret=secret)

    @Response.nacl_sign_open
    def nacl_sign_open(self, signed: Union[str, bytes], public: str) -> str:
        """
        :param signed: Base64 encoded signed data to be unsigned
        :param public: Signer's public key
        :return: Base64 encoded unsigned data
        """
        if type(signed) is bytes:
            signed = signed.decode()
        return self.request(
            method='crypto.nacl_sign_open', signed=signed,
            public=public)

    @Response.nacl_box_keypair
    def nacl_box_keypair(self) -> KeyPair:
        return self.request(method='crypto.nacl_box_keypair')

    @Response.nacl_box_keypair_from_secret_key
    def nacl_box_keypair_from_secret_key(self, secret: str) -> KeyPair:
        """
        Generates key pair from a secret key
        :param secret: Hex encoded secret key
        :return:
        """
        return self.request(
            method='crypto.nacl_box_keypair_from_secret_key',
            secret=secret)

    @Response.nacl_box
    def nacl_box(
            self, decrypted: Union[str, bytes], nonce: str, their_public: str,
            secret: str) -> str:
        """
        Public key authenticated encryption
        :param decrypted: Base64 encoded data to be encrypted
        :param nonce:
        :param their_public:
        :param secret:
        :return: Base64 encoded encrypted data
        """
        if type(decrypted) is bytes:
            decrypted = decrypted.decode()
        return self.request(
            method='crypto.nacl_box', decrypted=decrypted, nonce=nonce,
            their_public=their_public, secret=secret)

    @Response.nacl_box_open
    def nacl_box_open(
            self, encrypted: Union[str, bytes], nonce: str, their_public: str,
            secret: str) -> str:
        """
        Decrypt and verify the cipher text using the receiver's secret key
        and sender's public
        :param encrypted: Base64 encoded encrypted data to be decrypted
        :param nonce:
        :param their_public:
        :param secret:
        :return: Base64 encoded decrypted data
        """
        if type(encrypted) is bytes:
            encrypted = encrypted.decode()
        return self.request(
            method='crypto.nacl_box_open', encrypted=encrypted,
            nonce=nonce, their_public=their_public, secret=secret)

    @Response.nacl_secret_box
    def nacl_secret_box(
            self, decrypted: Union[str, bytes], nonce: str, key: str) -> str:
        """
        Encrypt and authenticate message using nonce and secret key
        :param decrypted: Base64 encoded data to be encrypted
        :param nonce:
        :param key:
        :return: Base64 encoded encrypted data
        """
        if type(decrypted) is bytes:
            decrypted = decrypted.decode()
        return self.request(
            method='crypto.nacl_secret_box', decrypted=decrypted,
            nonce=nonce, key=key)

    @Response.nacl_secret_box_open
    def nacl_secret_box_open(
            self, encrypted: Union[str, bytes], nonce: str, key: str) -> str:
        """
        Decrypts and verifies cipher text using nonce and secret key
        :param encrypted: Base64 encoded encrypted data to be decrypted
        :param nonce:
        :param key:
        :return: Base64 encoded decrypted data
        """
        if type(encrypted) is bytes:
            encrypted = encrypted.decode()
        return self.request(
            method='crypto.nacl_secret_box_open', encrypted=encrypted,
            nonce=nonce, key=key)

    @Response.scrypt
    def scrypt(
            self, password: Union[str, bytes], salt: Union[str, bytes],
            log_n: int, r: int, p: int, dk_len: int) -> str:
        """
        Derives key from 'password' and 'key' using 'scrypt' algorithm.
        See [https://en.wikipedia.org/wiki/Scrypt].
        :param password: Base64 encoded password
        :param salt: A base64 encoded salt bytes that modifies the hash to
                protect against Rainbow table attacks
        :param log_n: CPU/memory cost parameter
        :param r: The block size parameter, which fine-tunes sequential
                memory read size and performance (8 is commonly used)
        :param p: Parallelization parameter
        :param dk_len: Intended output length in octets of the derived key
        :return: Hex encoded derived key
        """
        if type(password) is bytes:
            password = password.decode()
        if type(salt) is bytes:
            salt = salt.decode()
        return self.request(
            method='crypto.scrypt', password=password, salt=salt,
            log_n=log_n, r=r, p=p, dk_len=dk_len)
