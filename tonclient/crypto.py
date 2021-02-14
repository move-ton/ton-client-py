from tonclient.module import TonModule
from tonclient.decorators import result_as
from tonclient.types import KeyPair, ParamsOfFactorize, ResultOfFactorize, \
    ParamsOfModularPower, ResultOfModularPower, ParamsOfTonCrc16, \
    ResultOfTonCrc16, ParamsOfGenerateRandomBytes, \
    ParamsOfConvertPublicKeyToTonSafeFormat, ResultOfGenerateRandomBytes, \
    ResultOfConvertPublicKeyToTonSafeFormat, ParamsOfSign, ResultOfSign, \
    ParamsOfVerifySignature, ResultOfVerifySignature, ParamsOfHash, \
    ResultOfHash, ParamsOfScrypt, ResultOfScrypt, \
    ParamsOfNaclSignKeyPairFromSecret, ParamsOfNaclSign, ResultOfNaclSign, \
    ParamsOfNaclSignOpen, ResultOfNaclSignOpen, ResultOfNaclSignDetached, \
    ParamsOfNaclBoxKeyPairFromSecret, ParamsOfNaclBox, ResultOfNaclBox, \
    ParamsOfNaclBoxOpen, ResultOfNaclBoxOpen, ParamsOfNaclSecretBox, \
    ParamsOfNaclSecretBoxOpen, ParamsOfMnemonicWords, ResultOfMnemonicWords, \
    ParamsOfMnemonicFromRandom, ResultOfMnemonicFromRandom, \
    ParamsOfMnemonicFromEntropy, ResultOfMnemonicFromEntropy, \
    ParamsOfMnemonicVerify, ResultOfMnemonicVerify, \
    ParamsOfMnemonicDeriveSignKeys, ParamsOfHDKeyXPrvFromMnemonic, \
    ResultOfHDKeyXPrvFromMnemonic, ParamsOfHDKeyDeriveFromXPrv, \
    ResultOfHDKeyDeriveFromXPrv, ParamsOfHDKeyDeriveFromXPrvPath, \
    ResultOfHDKeyDeriveFromXPrvPath, ParamsOfHDKeySecretFromXPrv, \
    ResultOfHDKeySecretFromXPrv, ParamsOfHDKeyPublicFromXPrv, \
    ResultOfHDKeyPublicFromXPrv, ParamsOfChaCha20, ResultOfChaCha20, \
    RegisteredSigningBox, ResultOfSigningBoxGetPublicKey, \
    ParamsOfSigningBoxSign, ResultOfSigningBoxSign, \
    ParamsOfNaclSignDetachedVerify, ResultOfNaclSignDetachedVerify, \
    ResponseHandler


class TonCrypto(TonModule):
    """ Free TON crypto SDK API implementation """
    @result_as(classname=ResultOfHash)
    def sha256(self, params: ParamsOfHash) -> ResultOfHash:
        """
        Calculates SHA256 hash of the specified data
        :param params: See `types.ParamsOfHash`
        :return: See `types.ResultOfHash`
        """
        return self.request(method='crypto.sha256', **params.dict)

    @result_as(classname=ResultOfHash)
    def sha512(self, params: ParamsOfHash) -> ResultOfHash:
        """
        Calculates SHA512 hash of the specified data
        :param params: See `types.ParamsOfHash`
        :return: See `types.ResultOfHash`
        """
        return self.request(method='crypto.sha512', **params.dict)

    @result_as(classname=ResultOfHDKeyXPrvFromMnemonic)
    def hdkey_xprv_from_mnemonic(
            self, params: ParamsOfHDKeyXPrvFromMnemonic
    ) -> ResultOfHDKeyXPrvFromMnemonic:
        """
        Generates an extended master private key that will be the root for all
        the derived keys
        :param params: See `types.ParamsOfHDKeyXPrvFromMnemonic`
        :return: See `types.ResultOfHDKeyXPrvFromMnemonic`
        """
        return self.request(
            method='crypto.hdkey_xprv_from_mnemonic', **params.dict)

    @result_as(classname=ResultOfHDKeySecretFromXPrv)
    def hdkey_secret_from_xprv(
            self, params: ParamsOfHDKeySecretFromXPrv
    ) -> ResultOfHDKeySecretFromXPrv:
        """
        Extracts the private key from the serialized extended private key
        :param params: See `types.ParamsOfHDKeySecretFromXPrv`
        :return: See `types.ResultOfHDKeySecretFromXPrv`
        """
        return self.request(
            method='crypto.hdkey_secret_from_xprv', **params.dict)

    @result_as(classname=ResultOfHDKeyPublicFromXPrv)
    def hdkey_public_from_xprv(
            self, params: ParamsOfHDKeyPublicFromXPrv
    ) -> ResultOfHDKeyPublicFromXPrv:
        """
        Extracts the public key from the serialized extended private key
        :param params: See `types.ParamsOfHDKeyPublicFromXPrv`
        :return: See `types.ResultOfHDKeyPublicFromXPrv`
        """
        return self.request(
            method='crypto.hdkey_public_from_xprv', **params.dict)

    @result_as(classname=ResultOfHDKeyDeriveFromXPrv)
    def hdkey_derive_from_xprv(
            self, params: ParamsOfHDKeyDeriveFromXPrv
    ) -> ResultOfHDKeyDeriveFromXPrv:
        """
        Returns extended private key derived from the specified extended
        private key and child index
        :param params: See `types.ParamsOfHDKeyDeriveFromXPrv`
        :return: See `types.ResultOfHDKeyDeriveFromXPrv`
        """
        return self.request(
            method='crypto.hdkey_derive_from_xprv', **params.dict)

    @result_as(classname=ResultOfHDKeyDeriveFromXPrvPath)
    def hdkey_derive_from_xprv_path(
            self, params: ParamsOfHDKeyDeriveFromXPrvPath
    ) -> ResultOfHDKeyDeriveFromXPrvPath:
        """
        Derives the extended private key from the specified key and path
        :param params: See `types.ParamsOfHDKeyDeriveFromXPrvPath`
        :return: See `types.ResultOfHDKeyDeriveFromXPrvPath`
        """
        return self.request(
            method='crypto.hdkey_derive_from_xprv_path', **params.dict)

    @result_as(classname=ResultOfConvertPublicKeyToTonSafeFormat)
    def convert_public_key_to_ton_safe_format(
            self, params: ParamsOfConvertPublicKeyToTonSafeFormat
    ) -> ResultOfConvertPublicKeyToTonSafeFormat:
        """
        Converts public key to ton safe_format
        :param params: See `types.ParamsOfConvertPublicKeyToTonSafeFormat`
        :return: See `types.ResultOfConvertPublicKeyToTonSafeFormat`
        """
        return self.request(
            method='crypto.convert_public_key_to_ton_safe_format',
            **params.dict)

    @result_as(classname=KeyPair)
    def generate_random_sign_keys(self) -> KeyPair:
        """
        Generates random ed25519 key pair
        :return: See `types.KeyPair`
        """
        return self.request(method='crypto.generate_random_sign_keys')

    @result_as(classname=ResultOfSign)
    def sign(self, params: ParamsOfSign) -> ResultOfSign:
        """
        Signs a data using the provided keys
        :param params: See `types.ParamsOfSign`
        :return: See `types.ResultOfSign`
        """
        return self.request(method='crypto.sign', **params.dict)

    @result_as(classname=ResultOfVerifySignature)
    def verify_signature(
            self, params: ParamsOfVerifySignature) -> ResultOfVerifySignature:
        """
        Verifies signed data using the provided public key.
        Raises error if verification is failed
        :param params: See `types.ParamsOfVerifySignature`
        :return: See `types.ResultOfVerifySignature`
        """
        return self.request(method='crypto.verify_signature', **params.dict)

    @result_as(classname=ResultOfModularPower)
    def modular_power(
            self, params: ParamsOfModularPower) -> ResultOfModularPower:
        """
        Performs modular exponentiation for big integers (`base`^`exponent`
        mod `modulus`).
        See [https://en.wikipedia.org/wiki/Modular_exponentiation]
        :param params: See `types.ParamsOfModularPower`
        :return: See `types.ResultOfModularPower`
        """
        return self.request(method='crypto.modular_power', **params.dict)

    @result_as(classname=ResultOfFactorize)
    def factorize(self, params: ParamsOfFactorize) -> ResultOfFactorize:
        """
        Performs prime factorization – decomposition of a composite number
        into a product of smaller prime integers (factors).
        See [https://en.wikipedia.org/wiki/Integer_factorization]
        :param params: See `types.ParamsOfFactorize`
        :return: See `types.ResultOfFactorize`
        """
        return self.request(method='crypto.factorize', **params.dict)

    @result_as(classname=ResultOfTonCrc16)
    def ton_crc16(self, params: ParamsOfTonCrc16) -> ResultOfTonCrc16:
        """
        Calculates CRC16 using TON algorithm
        :param params: See `types.ParamsOfTonCrc16`
        :return: See `types.ResultOfTonCrc16`
        """
        return self.request(method='crypto.ton_crc16', **params.dict)

    @result_as(classname=ResultOfGenerateRandomBytes)
    def generate_random_bytes(
            self, params: ParamsOfGenerateRandomBytes
    ) -> ResultOfGenerateRandomBytes:
        """
        Generates random byte array of the specified length and returns it
        in `base64` format
        :param params: See `types.ParamsOfGenerateRandomBytes`
        :return: See `types.ResultOfGenerateRandomBytes`
        """
        return self.request(
            method='crypto.generate_random_bytes', **params.dict)

    @result_as(classname=ResultOfMnemonicWords)
    def mnemonic_words(
            self, params: ParamsOfMnemonicWords) -> ResultOfMnemonicWords:
        """
        Prints the list of words from the specified dictionary
        :param params: See `types.ParamsOfMnemonicWords`
        :return: See `types.ResultOfMnemonicWords`
        """
        return self.request(method='crypto.mnemonic_words', **params.dict)

    @result_as(classname=ResultOfMnemonicFromRandom)
    def mnemonic_from_random(
            self, params: ParamsOfMnemonicFromRandom
    ) -> ResultOfMnemonicFromRandom:
        """
        Generates a random mnemonic from the specified dictionary
        and word count
        :param params: See `types.ParamsOfMnemonicFromRandom`
        :return: See `types.ResultOfMnemonicFromRandom`
        """
        return self.request(
            method='crypto.mnemonic_from_random', **params.dict)

    @result_as(classname=ResultOfMnemonicFromEntropy)
    def mnemonic_from_entropy(
            self, params: ParamsOfMnemonicFromEntropy
    ) -> ResultOfMnemonicFromEntropy:
        """
        Generates mnemonic from pre-generated entropy
        :param params: See `types.ParamsOfMnemonicFromEntropy`
        :return: See `types.ResultOfMnemonicFromEntropy`
        """
        return self.request(
            method='crypto.mnemonic_from_entropy', **params.dict)

    @result_as(classname=ResultOfMnemonicVerify)
    def mnemonic_verify(
            self, params: ParamsOfMnemonicVerify) -> ResultOfMnemonicVerify:
        """
        The phrase supplied will be checked for word length and validated
        according to the checksum specified in BIP0039
        :param params: See `types.ParamsOfMnemonicVerify`
        :return: See `types.ResultOfMnemonicVerify`
        """
        return self.request(method='crypto.mnemonic_verify', **params.dict)

    @result_as(classname=KeyPair)
    def mnemonic_derive_sign_keys(
            self, params: ParamsOfMnemonicDeriveSignKeys) -> KeyPair:
        """
        Validates the seed phrase, generates master key and then derives
        the key pair from the master key and the specified path
        :param params: See `types.ParamsOfMnemonicDeriveSignKeys`
        :return: See `types.KeyPair`
        """
        return self.request(
            method='crypto.mnemonic_derive_sign_keys', **params.dict)

    @result_as(classname=KeyPair)
    def nacl_sign_keypair_from_secret_key(
            self, params: ParamsOfNaclSignKeyPairFromSecret) -> KeyPair:
        """
        Generates a key pair for signing from the secret key
        :param params: See `types.ParamsOfNaclSignKeyPairFromSecret`
        :return: See `types.KeyPair`
        """
        return self.request(
            method='crypto.nacl_sign_keypair_from_secret_key', **params.dict)

    @result_as(classname=ResultOfNaclSign)
    def nacl_sign(self, params: ParamsOfNaclSign) -> ResultOfNaclSign:
        """
        Signs data using the signer's secret key
        :param params: See `types.ParamsOfNaclSign`
        :return: See `types.ResultOfNaclSign`
        """
        return self.request(method='crypto.nacl_sign', **params.dict)

    @result_as(classname=ResultOfNaclSignDetached)
    def nacl_sign_detached(
            self, params: ParamsOfNaclSign) -> ResultOfNaclSignDetached:
        """
        Signs the message using the secret key and returns a signature.
        Signs the message unsigned using the secret key `secret` and returns a
        signature `signature`
        :param params: See `types.ParamsOfNaclSign`
        :return: See `types.ResultOfNaclSignDetached`
        """
        return self.request(method='crypto.nacl_sign_detached', **params.dict)

    @result_as(classname=ResultOfNaclSignDetachedVerify)
    def nacl_sign_detached_verify(
            self, params: ParamsOfNaclSignDetachedVerify
    ) -> ResultOfNaclSignDetachedVerify:
        """
        Verifies the signature with public key and unsigned data
        :param params: See `types.ParamsOfNaclSignDetachedVerify`
        :return: See `types.ResultOfNaclSignDetachedVerify`
        """
        return self.request(
            method='crypto.nacl_sign_detached_verify', **params.dict)

    @result_as(classname=ResultOfNaclSignOpen)
    def nacl_sign_open(
            self, params: ParamsOfNaclSignOpen) -> ResultOfNaclSignOpen:
        """
        Verifies the signature and returns the unsigned message.
        Verifies the signature in `signed` using the signer's public key
        `public` and returns the message `unsigned`.
        If the signature fails verification, raises an exception
        :param params: See `types.ParamsOfNaclSignOpen`
        :return: See `types.ResultOfNaclSignOpen`
        """
        return self.request(method='crypto.nacl_sign_open', **params.dict)

    @result_as(classname=KeyPair)
    def nacl_box_keypair(self) -> KeyPair:
        """ Generates a random NaCl key pair """
        return self.request(method='crypto.nacl_box_keypair')

    @result_as(classname=KeyPair)
    def nacl_box_keypair_from_secret_key(
            self, params: ParamsOfNaclBoxKeyPairFromSecret) -> KeyPair:
        """
        Generates key pair from a secret key
        :param params: See `types.ParamsOfNaclBoxKeyPairFromSecret`
        :return: See `types.KeyPair`
        """
        return self.request(
            method='crypto.nacl_box_keypair_from_secret_key', **params.dict)

    @result_as(classname=ResultOfNaclBox)
    def nacl_box(self, params: ParamsOfNaclBox) -> ResultOfNaclBox:
        """
        Public key authenticated encryption.
        Encrypt and authenticate a message using the senders secret key,
        the receivers public key, and a nonce
        :param params: See `types.ParamsOfNaclBox`
        :return: See `types.ResultOfNaclBox`
        """
        return self.request(method='crypto.nacl_box', **params.dict)

    @result_as(classname=ResultOfNaclBoxOpen)
    def nacl_box_open(
            self, params: ParamsOfNaclBoxOpen) -> ResultOfNaclBoxOpen:
        """
        Decrypt and verify the cipher text using the receivers secret key,
        the senders public key, and the nonce
        :param params: See `types.ParamsOfNaclBoxOpen`
        :return: See `types.ResultOfNaclBoxOpen`
        """
        return self.request(method='crypto.nacl_box_open', **params.dict)

    @result_as(classname=ResultOfNaclBox)
    def nacl_secret_box(
            self, params: ParamsOfNaclSecretBox) -> ResultOfNaclBox:
        """
        Encrypt and authenticate message using nonce and secret key
        :param params: See `types.ParamsOfNaclSecretBox`
        :return: See `types.ResultOfNaclBox`
        """
        return self.request(method='crypto.nacl_secret_box', **params.dict)

    @result_as(classname=ResultOfNaclBoxOpen)
    def nacl_secret_box_open(
            self, params: ParamsOfNaclSecretBoxOpen) -> ResultOfNaclBoxOpen:
        """
        Decrypts and verifies cipher text using `nonce` and secret `key`
        :param params: See `types.ParamsOfNaclSecretBoxOpen`
        :return: See `types.ResultOfNaclBoxOpen`
        """
        return self.request(
            method='crypto.nacl_secret_box_open', **params.dict)

    @result_as(classname=ResultOfScrypt)
    def scrypt(self, params: ParamsOfScrypt) -> ResultOfScrypt:
        """
        Derives key from `password` and `key` using `scrypt` algorithm.
        See [https://en.wikipedia.org/wiki/Scrypt].
        :param params: See `types.ParamsOfScrypt`
        :return: See `types.ResultOfScrypt`
        """
        return self.request(method='crypto.scrypt', **params.dict)

    @result_as(classname=ResultOfChaCha20)
    def chacha20(self, params: ParamsOfChaCha20) -> ResultOfChaCha20:
        """
        Performs symmetric `chacha20` encryption
        :param params: See `types.ParamsOfChaCha20`
        :return: See `types.ResultOfChaCha20`
        """
        return self.request(method='crypto.chacha20', **params.dict)

    @result_as(classname=RegisteredSigningBox)
    def register_signing_box(
            self, callback: ResponseHandler) -> RegisteredSigningBox:
        """
        Register an application implemented signing box
        :param callback: Callback to send events to
        :return: See `types.RegisteredSigningBox`
        """
        return self.request(
            method='crypto.register_signing_box', callback=callback)

    @result_as(classname=RegisteredSigningBox)
    def get_signing_box(self, params: KeyPair) -> RegisteredSigningBox:
        """
        Creates a default signing box implementation
        :param params: See `types.KeyPair`
        :return: See `types.RegisteredSigningBox`
        """
        return self.request(method='crypto.get_signing_box', **params.dict)

    @result_as(classname=ResultOfSigningBoxGetPublicKey)
    def signing_box_get_public_key(
            self, params: RegisteredSigningBox
    ) -> ResultOfSigningBoxGetPublicKey:
        """
        Returns public key of signing key pair
        :param params: See `types.RegisteredSigningBox`
        :return: See `types.ResultOfSigningBoxGetPublicKey`
        """
        return self.request(
            method='crypto.signing_box_get_public_key', **params.dict)

    @result_as(classname=ResultOfSigningBoxSign)
    def signing_box_sign(
            self, params: ParamsOfSigningBoxSign) -> ResultOfSigningBoxSign:
        """
        Returns signed user data
        :param params: See `types.ParamsOfSigningBoxSign`
        :return: See `types.ResultOfSigningBoxSign`
        """
        return self.request(method='crypto.signing_box_sign', **params.dict)

    def remove_signing_box(self, params: RegisteredSigningBox):
        """
        Removes signing box from SDK
        :param params: See `types.RegisteredSigningBox`
        :return:
        """
        return self.request(method='crypto.remove_signing_box', **params.dict)
