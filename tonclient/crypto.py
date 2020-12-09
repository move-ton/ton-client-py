from typing import Dict, Union, List

from tonclient.decorators import Response
from tonclient.module import TonModule
from tonclient.types import KeyPair


class TonCrypto(TonModule):
    """ Free TON crypto SDK API implementation """
    @Response.sha256
    def sha256(self, data: Union[str, bytes]) -> str:
        """
        Calculates SHA256 hash of the specified data
        :param data: Input data for hash calculation encoded with `base64`
        :return:
        """
        if type(data) is bytes:
            data = data.decode()
        return self.request(method='crypto.sha256', data=data)

    @Response.sha512
    def sha512(self, data: Union[str, bytes]) -> str:
        """
        Calculates SHA512 hash of the specified data
        :param data: Input data for hash calculation encoded with `base64`
        :return:
        """
        if type(data) is bytes:
            data = data.decode()
        return self.request(method='crypto.sha512', data=data)

    @Response.hdkey_xprv_from_mnemonic
    def hdkey_xprv_from_mnemonic(
            self, phrase: str, dictionary: int = None, word_count: int = None
    ) -> str:
        """
        Generates an extended master private key that will be the root for all
        the derived keys
        :param phrase: String with seed phrase
        :param dictionary: Dictionary identifier
        :param word_count: Mnemonic word count
        :return:
        """
        return self.request(
            method='crypto.hdkey_xprv_from_mnemonic', phrase=phrase,
            dictionary=dictionary, word_count=word_count)

    @Response.hdkey_secret_from_xprv
    def hdkey_secret_from_xprv(self, xprv: str) -> str:
        """
        Extracts the private key from the serialized extended private key
        :param xprv: Serialized extended private key
        :return:
        """
        return self.request(method='crypto.hdkey_secret_from_xprv', xprv=xprv)

    @Response.hdkey_public_from_xprv
    def hdkey_public_from_xprv(self, xprv: str) -> str:
        """
        Extracts the public key from the serialized extended private key
        :param xprv: Serialized extended private key
        :return:
        """
        return self.request(method='crypto.hdkey_public_from_xprv', xprv=xprv)

    @Response.hdkey_derive_from_xprv
    def hdkey_derive_from_xprv(
            self, xprv: str, child_index: int, hardened: bool) -> str:
        """
        Returns extended private key derived from the specified extended
        private key and child index
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
        Derives the extended private key from the specified key and path
        :param xprv: Serialized extended private key
        :param path: Derivation path, for instance "m/44'/396'/0'/0/0"
        :return:
        """
        return self.request(
            method='crypto.hdkey_derive_from_xprv_path', xprv=xprv, path=path)

    @Response.convert_public_key_to_ton_safe_format
    def convert_public_key_to_ton_safe_format(self, public_key: str) -> str:
        """
        Converts public key to ton safe_format
        :param public_key: Public key - 64 symbols `hex` string
        :return:
        """
        return self.request(
            method='crypto.convert_public_key_to_ton_safe_format',
            public_key=public_key)

    @Response.generate_random_sign_keys
    def generate_random_sign_keys(self) -> KeyPair:
        """
        Generates random ed25519 key pair
        :return:
        """
        return self.request(method='crypto.generate_random_sign_keys')

    def sign(
            self, unsigned: Union[str, bytes], keys: KeyPair
    ) -> Dict[str, str]:
        """
        Signs a data using the provided keys
        :param unsigned: Data that must be signed encoded in `base64`
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
        Raises error if verification is failed
        :param signed: Signed data that must be verified encoded in `base64`
        :param public: Signer's public key - 64 symbols `hex` string
        :return: Unsigned data encoded in `base64`
        """
        if type(signed) is bytes:
            signed = signed.decode()
        return self.request(
            method='crypto.verify_signature', signed=signed, public=public)

    @Response.modular_power
    def modular_power(self, base: str, exponent: str, modulus: str) -> str:
        """
        Performs modular exponentiation for big integers (`base`^`exponent`
        mod `modulus`).
        See [https://en.wikipedia.org/wiki/Modular_exponentiation]
        :param base: `base` argument of calculation
        :param exponent: `exponent` argument of calculation
        :param modulus: `modulus` argument of calculation
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
        :return: Two factors of composite or empty if composite can't be
                factorized
        """
        return self.request(method='crypto.factorize', composite=composite)

    @Response.ton_crc16
    def ton_crc16(self, data: Union[str, bytes]) -> int:
        """
        Calculates CRC16 using TON algorithm
        :param data: Input data for CRC calculation. Encoded with `base64`
        :return:
        """
        if type(data) is bytes:
            data = data.decode()
        return self.request(method='crypto.ton_crc16', data=data)

    @Response.generate_random_bytes
    def generate_random_bytes(self, length: int) -> str:
        """
        Generates random byte array of the specified length and returns it
        in `base64` format
        :param length: Size of random byte array
        :return: Generated bytes encoded in `base64`
        """
        return self.request(
            method='crypto.generate_random_bytes', length=length)

    @Response.mnemonic_words
    def mnemonic_words(self, dictionary: int = None) -> str:
        """
        Prints the list of words from the specified dictionary
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
        and word count
        :param dictionary: Dictionary identifier
        :param word_count: Mnemonic word count
        :return: String of mnemonic words
        """
        return self.request(
            method='crypto.mnemonic_from_random', dictionary=dictionary,
            word_count=word_count)

    @Response.mnemonic_from_entropy
    def mnemonic_from_entropy(
            self, entropy: str, dictionary: int = None, word_count: int = None
    ) -> str:
        """
        Generates mnemonic from pre-generated entropy
        :param entropy: Entropy bytes. `Hex` encoded
        :param dictionary: Dictionary identifier
        :param word_count: Mnemonic word count
        :return: String of mnemonic words
        """
        return self.request(
            method='crypto.mnemonic_from_entropy', entropy=entropy,
            dictionary=dictionary, word_count=word_count)

    @Response.mnemonic_verify
    def mnemonic_verify(
            self, phrase: str, dictionary: int = None, word_count: int = None
    ) -> bool:
        """
        The phrase supplied will be checked for word length and validated
        according to the checksum specified in BIP0039
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
        the key pair from the master key and the specified path
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
        Generates a key pair for signing from the secret key
        :param secret: Secret key - unprefixed 0-padded to 64 symbols `hex`
                string
        :return:
        """
        return self.request(
            method='crypto.nacl_sign_keypair_from_secret_key',
            secret=secret)

    @Response.nacl_sign
    def nacl_sign(self, unsigned: Union[str, bytes], secret: str) -> str:
        """
        Signs data using the signer's secret key
        :param unsigned: Data that must be signed encoded in `base64`
        :param secret: Signer's secret key - unprefixed 0-padded to 64 symbols
                `hex` string
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
        :param unsigned: Data that must be signed encoded in `base64`
        :param secret: Signer's secret key - unprefixed 0-padded to 64 symbols
                `hex` string
        :return: Signature encoded in `hex`
        """
        if type(unsigned) is bytes:
            unsigned = unsigned.decode()
        return self.request(
            method='crypto.nacl_sign_detached', unsigned=unsigned,
            secret=secret)

    @Response.nacl_sign_open
    def nacl_sign_open(self, signed: Union[str, bytes], public: str) -> str:
        """
        :param signed: Signed data that must be unsigned. Encoded with `base64`
        :param public: Signer's public key - unprefixed 0-padded to 64 symbols
                `hex` string
        :return: Unsigned data, encoded in `base64`
        """
        if type(signed) is bytes:
            signed = signed.decode()
        return self.request(
            method='crypto.nacl_sign_open', signed=signed, public=public)

    @Response.nacl_box_keypair
    def nacl_box_keypair(self) -> KeyPair:
        return self.request(method='crypto.nacl_box_keypair')

    @Response.nacl_box_keypair_from_secret_key
    def nacl_box_keypair_from_secret_key(self, secret: str) -> KeyPair:
        """
        Generates key pair from a secret key
        :param secret: Secret key - unprefixed 0-padded to 64 symbols `hex`
                string
        :return:
        """
        return self.request(
            method='crypto.nacl_box_keypair_from_secret_key', secret=secret)

    @Response.nacl_box
    def nacl_box(
            self, decrypted: Union[str, bytes], nonce: str, their_public: str,
            secret: str) -> str:
        """
        Public key authenticated encryption.
        Encrypt and authenticate a message using the senders secret key,
        the receivers public key, and a nonce
        :param decrypted: Data that must be encrypted encoded in `base64`
        :param nonce: Nonce, encoded in `hex`
        :param their_public: Receiver's public key - unprefixed 0-padded to
                64 symbols `hex` string
        :param secret: Sender's private key - unprefixed 0-padded to 64
                symbols `hex` string
        :return: Encrypted data encoded in `base64`
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
        Decrypt and verify the cipher text using the receivers secret key,
        the senders public key, and the nonce
        :param encrypted: Data that must be decrypted. Encoded with `base64`
        :param nonce: Nonce, encoded in `hex`
        :param their_public: Sender's public key - unprefixed 0-padded to
                64 symbols `hex` string
        :param secret: Receiver's private key - unprefixed 0-padded to 64
                symbols `hex` string
        :return: Decrypted data encoded in `base64`
        """
        if type(encrypted) is bytes:
            encrypted = encrypted.decode()
        return self.request(
            method='crypto.nacl_box_open', encrypted=encrypted, nonce=nonce,
            their_public=their_public, secret=secret)

    @Response.nacl_secret_box
    def nacl_secret_box(
            self, decrypted: Union[str, bytes], nonce: str, key: str) -> str:
        """
        Encrypt and authenticate message using nonce and secret key
        :param decrypted: Data that must be encrypted. Encoded with `base64`
        :param nonce: Nonce in `hex`
        :param key: Secret key - unprefixed 0-padded to 64 symbols `hex` string
        :return: Encrypted data encoded in `base64`
        """
        if type(decrypted) is bytes:
            decrypted = decrypted.decode()
        return self.request(
            method='crypto.nacl_secret_box', decrypted=decrypted, nonce=nonce,
            key=key)

    @Response.nacl_secret_box_open
    def nacl_secret_box_open(
            self, encrypted: Union[str, bytes], nonce: str, key: str) -> str:
        """
        Decrypts and verifies cipher text using nonce and secret key
        :param encrypted: Data that must be decrypted. Encoded with `base64`
        :param nonce: Nonce in `hex`
        :param key: Public key - unprefixed 0-padded to 64 symbols `hex` string
        :return: Decrypted data encoded in `base64`
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
        Derives key from `password` and `key` using `scrypt` algorithm.
        See [https://en.wikipedia.org/wiki/Scrypt].
        Arguments:
            - `log_n` - The log2 of the Scrypt parameter `N`
            - `r` - The Scrypt parameter `r`
            - `p` - The Scrypt parameter `p`
        Conditions:
            - `log_n` must be less than `64`
            - `r` must be greater than `0` and less than or equal
                    to `4294967295`
            - `p` must be greater than `0` and less than `4294967295`
        Recommended values sufficient for most use-cases:
            - `log_n = 15` (`n = 32768`)
            - `r = 8`
            - `p = 1`
        :param password: The password bytes to be hashed. Must be encoded
                with `base64`
        :param salt: A salt bytes that modifies the hash to protect against
                Rainbow table attacks. Must be encoded with `base64`
        :param log_n: CPU/memory cost parameter
        :param r: The block size parameter, which fine-tunes sequential memory
                read size and performance
        :param p: Parallelization parameter
        :param dk_len: Intended output length in octets of the derived key
        :return: Derived key encoded with `hex`
        """
        if type(password) is bytes:
            password = password.decode()
        if type(salt) is bytes:
            salt = salt.decode()
        return self.request(
            method='crypto.scrypt', password=password, salt=salt, log_n=log_n,
            r=r, p=p, dk_len=dk_len)

    @Response.chacha20
    def chacha20(
            self, data: Union[str, bytes], key: Union[str, bytes],
            nonce: Union[str, bytes]) -> str:
        """
        Performs symmetric `chacha20` encryption
        :param data: Source data to be encrypted or decrypted. Must be
                encoded with `base64`
        :param key: 256-bit key. Must be encoded with `hex`
        :param nonce: 96-bit nonce. Must be encoded with `hex`
        :return: Encrypted/decrypted data. Encoded with `base64`
        """
        if type(data) is bytes:
            data = data.decode()
        if type(key) is bytes:
            key = key.decode()
        if type(nonce) is bytes:
            nonce = nonce.decode()
        return self.request(
            method='crypto.chacha20', data=data, key=key, nonce=nonce)

    def register_signing_box(self):
        """
        Register an application implemented signing box
        :return:
        """
        return self.request(
            method='crypto.register_signing_box', as_iterable=True)

    @Response.get_signing_box
    def get_signing_box(self, keypair: KeyPair) -> int:
        """
        Creates a default signing box implementation
        :param keypair: Keypair
        :return:
        """
        return self.request(
            method='crypto.get_signing_box', params_or_str=keypair.dict)

    @Response.signing_box_get_public_key
    def signing_box_get_public_key(self, handle: int) -> str:
        """
        Returns public key of signing key pair
        :param handle: Signing box handle
        :return:
        """
        return self.request(
            method='crypto.signing_box_get_public_key', handle=handle)

    @Response.signing_box_sign
    def signing_box_sign(
            self, signing_box: int, unsigned: Union[str, bytes]) -> str:
        """
        Returns signed user data
        :param signing_box: Signing Box handle
        :param unsigned: Unsigned user data. Must be encoded with `base64`
        :return:
        """
        if type(unsigned) is bytes:
            unsigned = unsigned.decode()
        return self.request(
            method='crypto.signing_box_sign', signing_box=signing_box,
            unsigned=unsigned)

    def remove_signing_box(self, handle: int):
        """
        Removes signing box from SDK
        :param handle: Signing Box handle
        :return:
        """
        return self.request(method='crypto.remove_signing_box', handle=handle)
