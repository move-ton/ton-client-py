"""Crypto module methods"""
from typing import Union, Awaitable

from tonclient.module import TonModule
from tonclient.types import (
    KeyPair,
    ParamsOfCreateCryptoBox,
    ParamsOfFactorize,
    ParamsOfGetEncryptionBoxFromCryptoBox,
    ParamsOfGetSigningBoxFromCryptoBox,
    RegisteredCryptoBox,
    ResultOfFactorize,
    ParamsOfModularPower,
    ResultOfGetCryptoBoxInfo,
    ResultOfGetCryptoBoxSeedPhrase,
    ResultOfModularPower,
    ParamsOfTonCrc16,
    ResultOfTonCrc16,
    ParamsOfGenerateRandomBytes,
    ParamsOfConvertPublicKeyToTonSafeFormat,
    ResultOfGenerateRandomBytes,
    ResultOfConvertPublicKeyToTonSafeFormat,
    ParamsOfSign,
    ResultOfSign,
    ParamsOfVerifySignature,
    ResultOfVerifySignature,
    ParamsOfHash,
    ResultOfHash,
    ParamsOfScrypt,
    ResultOfScrypt,
    ParamsOfNaclSignKeyPairFromSecret,
    ParamsOfNaclSign,
    ResultOfNaclSign,
    ParamsOfNaclSignOpen,
    ResultOfNaclSignOpen,
    ResultOfNaclSignDetached,
    ParamsOfNaclBoxKeyPairFromSecret,
    ParamsOfNaclBox,
    ResultOfNaclBox,
    ParamsOfNaclBoxOpen,
    ResultOfNaclBoxOpen,
    ParamsOfNaclSecretBox,
    ParamsOfNaclSecretBoxOpen,
    ParamsOfMnemonicWords,
    ResultOfMnemonicWords,
    ParamsOfMnemonicFromRandom,
    ResultOfMnemonicFromRandom,
    ParamsOfMnemonicFromEntropy,
    ResultOfMnemonicFromEntropy,
    ParamsOfMnemonicVerify,
    ResultOfMnemonicVerify,
    ParamsOfMnemonicDeriveSignKeys,
    ParamsOfHDKeyXPrvFromMnemonic,
    ResultOfHDKeyXPrvFromMnemonic,
    ParamsOfHDKeyDeriveFromXPrv,
    ResultOfHDKeyDeriveFromXPrv,
    ParamsOfHDKeyDeriveFromXPrvPath,
    ResultOfHDKeyDeriveFromXPrvPath,
    ParamsOfHDKeySecretFromXPrv,
    ResultOfHDKeySecretFromXPrv,
    ParamsOfHDKeyPublicFromXPrv,
    ResultOfHDKeyPublicFromXPrv,
    ParamsOfChaCha20,
    ResultOfChaCha20,
    RegisteredSigningBox,
    ResultOfSigningBoxGetPublicKey,
    ParamsOfSigningBoxSign,
    ResultOfSigningBoxSign,
    ParamsOfNaclSignDetachedVerify,
    ResultOfNaclSignDetachedVerify,
    ResponseHandler,
    RegisteredEncryptionBox,
    ParamsOfEncryptionBoxGetInfo,
    ResultOfEncryptionBoxGetInfo,
    ParamsOfEncryptionBoxEncrypt,
    ResultOfEncryptionBoxEncrypt,
    ParamsOfEncryptionBoxDecrypt,
    ResultOfEncryptionBoxDecrypt,
    ParamsOfCreateEncryptionBox,
)


class TonCrypto(TonModule):
    """Free TON crypto SDK API implementation"""

    def sha256(
        self, params: ParamsOfHash
    ) -> Union[ResultOfHash, Awaitable[ResultOfHash]]:
        """
        Calculates SHA256 hash of the specified data

        :param params: See `types.ParamsOfHash`
        :return: See `types.ResultOfHash`
        """
        response = self.request(method='crypto.sha256', **params.dict)
        return self.response(classname=ResultOfHash, response=response)

    def sha512(
        self, params: ParamsOfHash
    ) -> Union[ResultOfHash, Awaitable[ResultOfHash]]:
        """
        Calculates SHA512 hash of the specified data

        :param params: See `types.ParamsOfHash`
        :return: See `types.ResultOfHash`
        """
        response = self.request(method='crypto.sha512', **params.dict)
        return self.response(classname=ResultOfHash, response=response)

    def hdkey_xprv_from_mnemonic(
        self, params: ParamsOfHDKeyXPrvFromMnemonic
    ) -> Union[ResultOfHDKeyXPrvFromMnemonic, Awaitable[ResultOfHDKeyXPrvFromMnemonic]]:
        """
        Generates an extended master private key that will be the root for all
        the derived keys

        :param params: See `types.ParamsOfHDKeyXPrvFromMnemonic`
        :return: See `types.ResultOfHDKeyXPrvFromMnemonic`
        """
        response = self.request(method='crypto.hdkey_xprv_from_mnemonic', **params.dict)
        return self.response(classname=ResultOfHDKeyXPrvFromMnemonic, response=response)

    def hdkey_secret_from_xprv(
        self, params: ParamsOfHDKeySecretFromXPrv
    ) -> Union[ResultOfHDKeySecretFromXPrv, Awaitable[ResultOfHDKeySecretFromXPrv]]:
        """
        Extracts the private key from the serialized extended private key

        :param params: See `types.ParamsOfHDKeySecretFromXPrv`
        :return: See `types.ResultOfHDKeySecretFromXPrv`
        """
        response = self.request(method='crypto.hdkey_secret_from_xprv', **params.dict)
        return self.response(classname=ResultOfHDKeySecretFromXPrv, response=response)

    def hdkey_public_from_xprv(
        self, params: ParamsOfHDKeyPublicFromXPrv
    ) -> Union[ResultOfHDKeyPublicFromXPrv, Awaitable[ResultOfHDKeyPublicFromXPrv]]:
        """
        Extracts the public key from the serialized extended private key

        :param params: See `types.ParamsOfHDKeyPublicFromXPrv`
        :return: See `types.ResultOfHDKeyPublicFromXPrv`
        """
        response = self.request(method='crypto.hdkey_public_from_xprv', **params.dict)
        return self.response(classname=ResultOfHDKeyPublicFromXPrv, response=response)

    def hdkey_derive_from_xprv(
        self, params: ParamsOfHDKeyDeriveFromXPrv
    ) -> Union[ResultOfHDKeyDeriveFromXPrv, Awaitable[ResultOfHDKeyDeriveFromXPrv]]:
        """
        Returns extended private key derived from the specified extended
        private key and child index

        :param params: See `types.ParamsOfHDKeyDeriveFromXPrv`
        :return: See `types.ResultOfHDKeyDeriveFromXPrv`
        """
        response = self.request(method='crypto.hdkey_derive_from_xprv', **params.dict)
        return self.response(classname=ResultOfHDKeyDeriveFromXPrv, response=response)

    def hdkey_derive_from_xprv_path(
        self, params: ParamsOfHDKeyDeriveFromXPrvPath
    ) -> Union[
        ResultOfHDKeyDeriveFromXPrvPath, Awaitable[ResultOfHDKeyDeriveFromXPrvPath]
    ]:
        """
        Derives the extended private key from the specified key and path

        :param params: See `types.ParamsOfHDKeyDeriveFromXPrvPath`
        :return: See `types.ResultOfHDKeyDeriveFromXPrvPath`
        """
        response = self.request(
            method='crypto.hdkey_derive_from_xprv_path', **params.dict
        )
        return self.response(
            classname=ResultOfHDKeyDeriveFromXPrvPath, response=response
        )

    def convert_public_key_to_ton_safe_format(
        self, params: ParamsOfConvertPublicKeyToTonSafeFormat
    ) -> Union[
        ResultOfConvertPublicKeyToTonSafeFormat,
        Awaitable[ResultOfConvertPublicKeyToTonSafeFormat],
    ]:
        """
        Converts public key to ton safe_format

        :param params: See `types.ParamsOfConvertPublicKeyToTonSafeFormat`
        :return: See `types.ResultOfConvertPublicKeyToTonSafeFormat`
        """
        response = self.request(
            method='crypto.convert_public_key_to_ton_safe_format', **params.dict
        )
        return self.response(
            classname=ResultOfConvertPublicKeyToTonSafeFormat, response=response
        )

    def generate_random_sign_keys(self) -> Union[KeyPair, Awaitable[KeyPair]]:
        """
        Generates random ed25519 key pair

        :return: See `types.KeyPair`
        """
        response = self.request(method='crypto.generate_random_sign_keys')
        return self.response(classname=KeyPair, response=response)

    def sign(
        self, params: ParamsOfSign
    ) -> Union[ResultOfSign, Awaitable[ResultOfSign]]:
        """
        Signs a data using the provided keys

        :param params: See `types.ParamsOfSign`
        :return: See `types.ResultOfSign`
        """
        response = self.request(method='crypto.sign', **params.dict)
        return self.response(classname=ResultOfSign, response=response)

    def verify_signature(
        self, params: ParamsOfVerifySignature
    ) -> Union[ResultOfVerifySignature, Awaitable[ResultOfVerifySignature]]:
        """
        Verifies signed data using the provided public key.
        Raises error if verification is failed

        :param params: See `types.ParamsOfVerifySignature`
        :return: See `types.ResultOfVerifySignature`
        """
        response = self.request(method='crypto.verify_signature', **params.dict)
        return self.response(classname=ResultOfVerifySignature, response=response)

    def modular_power(
        self, params: ParamsOfModularPower
    ) -> Union[ResultOfModularPower, Awaitable[ResultOfModularPower]]:
        """
        Performs modular exponentiation for big integers (`base`^`exponent`
        mod `modulus`).
        See [https://en.wikipedia.org/wiki/Modular_exponentiation]

        :param params: See `types.ParamsOfModularPower`
        :return: See `types.ResultOfModularPower`
        """
        response = self.request(method='crypto.modular_power', **params.dict)
        return self.response(classname=ResultOfModularPower, response=response)

    def factorize(
        self, params: ParamsOfFactorize
    ) -> Union[ResultOfFactorize, Awaitable[ResultOfFactorize]]:
        """
        Performs prime factorization – decomposition of a composite number
        into a product of smaller prime integers (factors).
        See [https://en.wikipedia.org/wiki/Integer_factorization]

        :param params: See `types.ParamsOfFactorize`
        :return: See `types.ResultOfFactorize`
        """
        response = self.request(method='crypto.factorize', **params.dict)
        return self.response(classname=ResultOfFactorize, response=response)

    def ton_crc16(
        self, params: ParamsOfTonCrc16
    ) -> Union[ResultOfTonCrc16, Awaitable[ResultOfTonCrc16]]:
        """
        Calculates CRC16 using TON algorithm

        :param params: See `types.ParamsOfTonCrc16`
        :return: See `types.ResultOfTonCrc16`
        """
        response = self.request(method='crypto.ton_crc16', **params.dict)
        return self.response(classname=ResultOfTonCrc16, response=response)

    def generate_random_bytes(
        self, params: ParamsOfGenerateRandomBytes
    ) -> Union[ResultOfGenerateRandomBytes, Awaitable[ResultOfGenerateRandomBytes]]:
        """
        Generates random byte array of the specified length and returns it
        in `base64` format

        :param params: See `types.ParamsOfGenerateRandomBytes`
        :return: See `types.ResultOfGenerateRandomBytes`
        """
        response = self.request(method='crypto.generate_random_bytes', **params.dict)
        return self.response(classname=ResultOfGenerateRandomBytes, response=response)

    def mnemonic_words(
        self, params: ParamsOfMnemonicWords
    ) -> Union[ResultOfMnemonicWords, Awaitable[ResultOfMnemonicWords]]:
        """
        Prints the list of words from the specified dictionary

        :param params: See `types.ParamsOfMnemonicWords`
        :return: See `types.ResultOfMnemonicWords`
        """
        response = self.request(method='crypto.mnemonic_words', **params.dict)
        return self.response(classname=ResultOfMnemonicWords, response=response)

    def mnemonic_from_random(
        self, params: ParamsOfMnemonicFromRandom
    ) -> Union[ResultOfMnemonicFromRandom, Awaitable[ResultOfMnemonicFromRandom]]:
        """
        Generates a random mnemonic from the specified dictionary
        and word count

        :param params: See `types.ParamsOfMnemonicFromRandom`
        :return: See `types.ResultOfMnemonicFromRandom`
        """
        response = self.request(method='crypto.mnemonic_from_random', **params.dict)
        return self.response(classname=ResultOfMnemonicFromRandom, response=response)

    def mnemonic_from_entropy(
        self, params: ParamsOfMnemonicFromEntropy
    ) -> Union[ResultOfMnemonicFromEntropy, Awaitable[ResultOfMnemonicFromEntropy]]:
        """
        Generates mnemonic from pre-generated entropy

        :param params: See `types.ParamsOfMnemonicFromEntropy`
        :return: See `types.ResultOfMnemonicFromEntropy`
        """
        response = self.request(method='crypto.mnemonic_from_entropy', **params.dict)
        return self.response(classname=ResultOfMnemonicFromEntropy, response=response)

    def mnemonic_verify(
        self, params: ParamsOfMnemonicVerify
    ) -> Union[ResultOfMnemonicVerify, Awaitable[ResultOfMnemonicVerify]]:
        """
        The phrase supplied will be checked for word length and validated
        according to the checksum specified in BIP0039

        :param params: See `types.ParamsOfMnemonicVerify`
        :return: See `types.ResultOfMnemonicVerify`
        """
        response = self.request(method='crypto.mnemonic_verify', **params.dict)
        return self.response(classname=ResultOfMnemonicVerify, response=response)

    def mnemonic_derive_sign_keys(
        self, params: ParamsOfMnemonicDeriveSignKeys
    ) -> Union[KeyPair, Awaitable[KeyPair]]:
        """
        Validates the seed phrase, generates master key and then derives
        the key pair from the master key and the specified path

        :param params: See `types.ParamsOfMnemonicDeriveSignKeys`
        :return: See `types.KeyPair`
        """
        response = self.request(
            method='crypto.mnemonic_derive_sign_keys', **params.dict
        )
        return self.response(classname=KeyPair, response=response)

    def nacl_sign_keypair_from_secret_key(
        self, params: ParamsOfNaclSignKeyPairFromSecret
    ) -> Union[KeyPair, Awaitable[KeyPair]]:
        """
        Generates a key pair for signing from the secret key.
        NOTE: In the result the secret key is actually the concatenation of
        secret and public keys (128 symbols hex string) by design of NaCL.
        See also the https://crypto.stackexchange.com/questions/54353/

        :param params: See `types.ParamsOfNaclSignKeyPairFromSecret`
        :return: See `types.KeyPair`
        """
        response = self.request(
            method='crypto.nacl_sign_keypair_from_secret_key', **params.dict
        )
        return self.response(classname=KeyPair, response=response)

    def nacl_sign(
        self, params: ParamsOfNaclSign
    ) -> Union[ResultOfNaclSign, Awaitable[ResultOfNaclSign]]:
        """
        Signs data using the signer's secret key

        :param params: See `types.ParamsOfNaclSign`
        :return: See `types.ResultOfNaclSign`
        """
        response = self.request(method='crypto.nacl_sign', **params.dict)
        return self.response(classname=ResultOfNaclSign, response=response)

    def nacl_sign_detached(
        self, params: ParamsOfNaclSign
    ) -> Union[ResultOfNaclSignDetached, Awaitable[ResultOfNaclSignDetached]]:
        """
        Signs the message using the secret key and returns a signature.
        Signs the message unsigned using the secret key `secret` and returns a
        signature `signature`

        :param params: See `types.ParamsOfNaclSign`
        :return: See `types.ResultOfNaclSignDetached`
        """
        response = self.request(method='crypto.nacl_sign_detached', **params.dict)
        return self.response(classname=ResultOfNaclSignDetached, response=response)

    def nacl_sign_detached_verify(
        self, params: ParamsOfNaclSignDetachedVerify
    ) -> Union[
        ResultOfNaclSignDetachedVerify, Awaitable[ResultOfNaclSignDetachedVerify]
    ]:
        """
        Verifies the signature with public key and unsigned data

        :param params: See `types.ParamsOfNaclSignDetachedVerify`
        :return: See `types.ResultOfNaclSignDetachedVerify`
        """
        response = self.request(
            method='crypto.nacl_sign_detached_verify', **params.dict
        )
        return self.response(
            classname=ResultOfNaclSignDetachedVerify, response=response
        )

    def nacl_sign_open(
        self, params: ParamsOfNaclSignOpen
    ) -> Union[ResultOfNaclSignOpen, Awaitable[ResultOfNaclSignOpen]]:
        """
        Verifies the signature and returns the unsigned message.
        Verifies the signature in `signed` using the signer's public key
        `public` and returns the message `unsigned`.
        If the signature fails verification, raises an exception

        :param params: See `types.ParamsOfNaclSignOpen`
        :return: See `types.ResultOfNaclSignOpen`
        """
        response = self.request(method='crypto.nacl_sign_open', **params.dict)
        return self.response(classname=ResultOfNaclSignOpen, response=response)

    def nacl_box_keypair(self) -> Union[KeyPair, Awaitable[KeyPair]]:
        """Generates a random NaCl key pair"""
        response = self.request(method='crypto.nacl_box_keypair')
        return self.response(classname=KeyPair, response=response)

    def nacl_box_keypair_from_secret_key(
        self, params: ParamsOfNaclBoxKeyPairFromSecret
    ) -> Union[KeyPair, Awaitable[KeyPair]]:
        """
        Generates key pair from a secret key

        :param params: See `types.ParamsOfNaclBoxKeyPairFromSecret`
        :return: See `types.KeyPair`
        """
        response = self.request(
            method='crypto.nacl_box_keypair_from_secret_key', **params.dict
        )
        return self.response(classname=KeyPair, response=response)

    def nacl_box(
        self, params: ParamsOfNaclBox
    ) -> Union[ResultOfNaclBox, Awaitable[ResultOfNaclBox]]:
        """
        Public key authenticated encryption.
        Encrypt and authenticate a message using the senders secret key,
        the receivers public key, and a nonce

        :param params: See `types.ParamsOfNaclBox`
        :return: See `types.ResultOfNaclBox`
        """
        response = self.request(method='crypto.nacl_box', **params.dict)
        return self.response(classname=ResultOfNaclBox, response=response)

    def nacl_box_open(
        self, params: ParamsOfNaclBoxOpen
    ) -> Union[ResultOfNaclBoxOpen, Awaitable[ResultOfNaclBoxOpen]]:
        """
        Decrypt and verify the cipher text using the receivers secret key,
        the senders public key, and the nonce

        :param params: See `types.ParamsOfNaclBoxOpen`
        :return: See `types.ResultOfNaclBoxOpen`
        """
        response = self.request(method='crypto.nacl_box_open', **params.dict)
        return self.response(classname=ResultOfNaclBoxOpen, response=response)

    def nacl_secret_box(
        self, params: ParamsOfNaclSecretBox
    ) -> Union[ResultOfNaclBox, Awaitable[ResultOfNaclBox]]:
        """
        Encrypt and authenticate message using nonce and secret key

        :param params: See `types.ParamsOfNaclSecretBox`
        :return: See `types.ResultOfNaclBox`
        """
        response = self.request(method='crypto.nacl_secret_box', **params.dict)
        return self.response(classname=ResultOfNaclBox, response=response)

    def nacl_secret_box_open(
        self, params: ParamsOfNaclSecretBoxOpen
    ) -> Union[ResultOfNaclBoxOpen, Awaitable[ResultOfNaclBoxOpen]]:
        """
        Decrypts and verifies cipher text using `nonce` and secret `key`

        :param params: See `types.ParamsOfNaclSecretBoxOpen`
        :return: See `types.ResultOfNaclBoxOpen`
        """
        response = self.request(method='crypto.nacl_secret_box_open', **params.dict)
        return self.response(classname=ResultOfNaclBoxOpen, response=response)

    def scrypt(
        self, params: ParamsOfScrypt
    ) -> Union[ResultOfScrypt, Awaitable[ResultOfScrypt]]:
        """
        Derives key from `password` and `key` using `scrypt` algorithm.
        See [https://en.wikipedia.org/wiki/Scrypt].

        :param params: See `types.ParamsOfScrypt`
        :return: See `types.ResultOfScrypt`
        """
        response = self.request(method='crypto.scrypt', **params.dict)
        return self.response(classname=ResultOfScrypt, response=response)

    def chacha20(
        self, params: ParamsOfChaCha20
    ) -> Union[ResultOfChaCha20, Awaitable[ResultOfChaCha20]]:
        """
        Performs symmetric `chacha20` encryption

        :param params: See `types.ParamsOfChaCha20`
        :return: See `types.ResultOfChaCha20`
        """
        response = self.request(method='crypto.chacha20', **params.dict)
        return self.response(classname=ResultOfChaCha20, response=response)

    def register_signing_box(
        self, callback: ResponseHandler
    ) -> Union[RegisteredSigningBox, Awaitable[RegisteredSigningBox]]:
        """
        Register an application implemented signing box

        :param callback: Callback to send events to
        :return: See `types.RegisteredSigningBox`
        """
        response = self.request(method='crypto.register_signing_box', callback=callback)
        return self.response(classname=RegisteredSigningBox, response=response)

    def get_signing_box(
        self, params: KeyPair
    ) -> Union[RegisteredSigningBox, Awaitable[RegisteredSigningBox]]:
        """
        Creates a default signing box implementation

        :param params: See `types.KeyPair`
        :return: See `types.RegisteredSigningBox`
        """
        response = self.request(method='crypto.get_signing_box', **params.dict)
        return self.response(classname=RegisteredSigningBox, response=response)

    def signing_box_get_public_key(
        self, params: RegisteredSigningBox
    ) -> Union[
        ResultOfSigningBoxGetPublicKey, Awaitable[ResultOfSigningBoxGetPublicKey]
    ]:
        """
        Returns public key of signing key pair

        :param params: See `types.RegisteredSigningBox`
        :return: See `types.ResultOfSigningBoxGetPublicKey`
        """
        response = self.request(
            method='crypto.signing_box_get_public_key', **params.dict
        )
        return self.response(
            classname=ResultOfSigningBoxGetPublicKey, response=response
        )

    def signing_box_sign(
        self, params: ParamsOfSigningBoxSign
    ) -> Union[ResultOfSigningBoxSign, Awaitable[ResultOfSigningBoxSign]]:
        """
        Returns signed user data

        :param params: See `types.ParamsOfSigningBoxSign`
        :return: See `types.ResultOfSigningBoxSign`
        """
        response = self.request(method='crypto.signing_box_sign', **params.dict)
        return self.response(classname=ResultOfSigningBoxSign, response=response)

    def remove_signing_box(
        self, params: RegisteredSigningBox
    ) -> Union[None, Awaitable[None]]:
        """
        Removes signing box from SDK

        :param params: See `types.RegisteredSigningBox`
        :return:
        """
        return self.request(method='crypto.remove_signing_box', **params.dict)

    def register_encryption_box(
        self, callback: ResponseHandler
    ) -> Union[RegisteredEncryptionBox, Awaitable[RegisteredEncryptionBox]]:
        """
        Register an application implemented encryption box

        :param callback: Callback to send events to
        :return: See `types.RegisteredEncryptionBox`
        """
        response = self.request(
            method='crypto.register_encryption_box', callback=callback
        )
        return self.response(classname=RegisteredEncryptionBox, response=response)

    def remove_encryption_box(
        self, params: RegisteredEncryptionBox
    ) -> Union[None, Awaitable[None]]:
        """Removes encryption box from SDK"""
        return self.request(method='crypto.remove_encryption_box', **params.dict)

    def encryption_box_get_info(
        self, params: ParamsOfEncryptionBoxGetInfo
    ) -> Union[ResultOfEncryptionBoxGetInfo, Awaitable[ResultOfEncryptionBoxGetInfo]]:
        """
        Queries info from the given encryption box

        :param params: See `types.ParamsOfEncryptionBoxGetInfo`
        :return: See `types.ResultOfEncryptionBoxGetInfo`
        """
        response = self.request(method='crypto.encryption_box_get_info', **params.dict)
        return self.response(classname=ResultOfEncryptionBoxGetInfo, response=response)

    def encryption_box_encrypt(
        self, params: ParamsOfEncryptionBoxEncrypt
    ) -> Union[ResultOfEncryptionBoxEncrypt, Awaitable[ResultOfEncryptionBoxEncrypt]]:
        """
        Encrypts data using given encryption box Note.
        Block cipher algorithms pad data to cipher block size so encrypted
        data can be longer then original data. Client should store the
        original data size after encryption and use it after decryption
        to retrieve the original data from decrypted data

        :param params: See `types.ParamsOfEncryptionBoxEncrypt`
        :return: See `types.ResultOfEncryptionBoxEncrypt`
        """
        response = self.request(method='crypto.encryption_box_encrypt', **params.dict)
        return self.response(classname=ResultOfEncryptionBoxEncrypt, response=response)

    def encryption_box_decrypt(
        self, params: ParamsOfEncryptionBoxDecrypt
    ) -> Union[ResultOfEncryptionBoxDecrypt, Awaitable[ResultOfEncryptionBoxDecrypt]]:
        """
        Decrypts data using given encryption box Note.
        Block cipher algorithms pad data to cipher block size so encrypted
        data can be longer then original data. Client should store the
        original data size after encryption and use it after decryption
        to retrieve the original data from decrypted data

        :param params: See `types.ParamsOfEncryptionBoxDecrypt`
        :return: See `types.ResultOfEncryptionBoxDecrypt`
        """
        response = self.request(method='crypto.encryption_box_decrypt', **params.dict)
        return self.response(classname=ResultOfEncryptionBoxDecrypt, response=response)

    def create_encryption_box(
        self, params: ParamsOfCreateEncryptionBox
    ) -> Union[RegisteredEncryptionBox, Awaitable[RegisteredEncryptionBox]]:
        """
        Creates encryption box with specified algorithm

        :param params: See `types.ParamsOfCreateEncryptionBox`
        :return: See `types.RegisteredEncryptionBox`
        """
        response = self.request(method='crypto.create_encryption_box', **params.dict)
        return self.response(classname=RegisteredEncryptionBox, response=response)

    def create_crypto_box(
        self, params: ParamsOfCreateCryptoBox, callback: ResponseHandler
    ) -> Union[RegisteredCryptoBox, Awaitable[RegisteredCryptoBox]]:
        """
        Creates a Crypto Box instance.

        Crypto Box is a root crypto object, that encapsulates some
        secret (seed phrase usually) in encrypted form and acts as a
        factory for all crypto primitives used in SDK: keys for signing
        and encryption, derived from this secret.

        Crypto Box encrypts original Seed Phrase with salt and password
        that is retrieved from `password_provider` callback, implemented
        on Application side.

        When used, decrypted secret shows up in core library's memory for a
        very short period of time and then is immediately overwritten
        with zeroes

        :param params: See `types.ParamsOfCreateCryptoBox`
        :param callback: Callback to send events to
        :return: See `types.RegisteredCryptoBox`
        """
        response = self.request(
            method='crypto.create_crypto_box', **params.dict, callback=callback
        )
        return self.response(classname=RegisteredCryptoBox, response=response)

    def remove_crypto_box(
        self, params: RegisteredCryptoBox
    ) -> Union[None, Awaitable[None]]:
        """
        Removes Crypto Box. Clears all secret data.

        :param params: See `types.RegisteredCryptoBox`
        """
        return self.request(method='crypto.remove_crypto_box', **params.dict)

    def get_crypto_box_info(
        self, params: RegisteredCryptoBox
    ) -> Union[ResultOfGetCryptoBoxInfo, Awaitable[ResultOfGetCryptoBoxInfo]]:
        """
        Get Crypto Box Info.
        Used to get `encrypted_secret` that should be used for all
        the cryptobox initializations except the first one

        :param params: See `types.RegisteredCryptoBox`
        :return: See `types.ResultOfGetCryptoBoxInfo`
        """
        response = self.request(method='crypto.get_crypto_box_info', **params.dict)
        return self.response(classname=ResultOfGetCryptoBoxInfo, response=response)

    def get_crypto_box_seed_phrase(
        self, params: RegisteredCryptoBox
    ) -> Union[
        ResultOfGetCryptoBoxSeedPhrase, Awaitable[ResultOfGetCryptoBoxSeedPhrase]
    ]:
        """
        Get Crypto Box Seed Phrase.

        Attention! Store this data in your application for a very
        short period of time and overwrite it with zeroes ASAP

        :param params: See `types.RegisteredCryptoBox`
        :return: See `types.ResultOfGetCryptoBoxSeedPhrase`
        """
        response = self.request(
            method='crypto.get_crypto_box_seed_phrase', **params.dict
        )
        return self.response(
            classname=ResultOfGetCryptoBoxSeedPhrase, response=response
        )

    def get_signing_box_from_crypto_box(
        self, params: ParamsOfGetSigningBoxFromCryptoBox
    ) -> Union[RegisteredSigningBox, Awaitable[RegisteredSigningBox]]:
        """
        Get handle of Signing Box derived from Crypto Box

        :param params: See `types.ParamsOfGetSigningBoxFromCryptoBox`
        :return: See `types.RegisteredSigningBox`
        """
        response = self.request(
            method='crypto.get_signing_box_from_crypto_box', **params.dict
        )
        return self.response(classname=RegisteredSigningBox, response=response)

    def get_encryption_box_from_crypto_box(
        self, params: ParamsOfGetEncryptionBoxFromCryptoBox
    ) -> Union[RegisteredEncryptionBox, Awaitable[RegisteredEncryptionBox]]:
        """
        Gets Encryption Box from Crypto Box.
        Derives encryption keypair from cryptobox secret and hdpath and
        stores it in cache for secret_lifetime or until explicitly cleared
        by `clear_crypto_box_secret_cache` method.
        If `secret_lifetime` is not specified - overwrites encryption secret
        with zeroes immediately after encryption operation.

        :param params: See `types.ParamsOfGetEncryptionBoxFromCryptoBox`
        :return: See `types.RegisteredEncryptionBox`
        """
        response = self.request(
            method='crypto.get_encryption_box_from_crypto_box', **params.dict
        )
        return self.response(classname=RegisteredEncryptionBox, response=response)

    def clear_crypto_box_secret_cache(
        self, params: RegisteredCryptoBox
    ) -> Union[None, Awaitable[None]]:
        """
        Removes cached secrets (overwrites with zeroes) from all
        signing and encryption boxes, derived from crypto box

        :param params: See `types.RegisteredCryptoBox`
        """
        return self.request(
            method='crypto.clear_crypto_box_secret_cache', **params.dict
        )
