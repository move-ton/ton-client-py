import base64

import unittest

from tonclient.errors import TonException
from tonclient.test.helpers import async_core_client, sync_core_client
from tonclient.types import KeyPair, MnemonicDictionary, ParamsOfHash, \
    ParamsOfHDKeyXPrvFromMnemonic, ParamsOfHDKeySecretFromXPrv, \
    ParamsOfHDKeyPublicFromXPrv, ParamsOfHDKeyDeriveFromXPrv, \
    ParamsOfHDKeyDeriveFromXPrvPath, ParamsOfConvertPublicKeyToTonSafeFormat, \
    ParamsOfSign, ParamsOfVerifySignature, ParamsOfModularPower, \
    ParamsOfFactorize, ParamsOfTonCrc16, ParamsOfGenerateRandomBytes, \
    ParamsOfMnemonicWords, ParamsOfMnemonicFromRandom, \
    ParamsOfMnemonicFromEntropy, ParamsOfMnemonicVerify, \
    ParamsOfMnemonicDeriveSignKeys, ParamsOfNaclSignKeyPairFromSecret, \
    ParamsOfNaclSign, ParamsOfNaclSignOpen, ParamsOfNaclBoxKeyPairFromSecret, \
    ParamsOfNaclBox, ParamsOfNaclBoxOpen, ParamsOfNaclSecretBox, \
    ParamsOfNaclSecretBoxOpen, ParamsOfScrypt, ParamsOfChaCha20, \
    ParamsOfSigningBoxSign, ParamsOfAppRequest, ParamsOfAppSigningBox, \
    ParamsOfResolveAppRequest, ResultOfAppSigningBox, AppRequestResult, \
    ParamsOfNaclSignDetachedVerify, ParamsOfEncryptionBoxGetInfo, \
    ParamsOfAppEncryptionBox, ResultOfAppEncryptionBox, EncryptionBoxInfo, \
    ParamsOfEncryptionBoxEncrypt, ParamsOfEncryptionBoxDecrypt


class TestTonCryptoAsyncCore(unittest.TestCase):
    def setUp(self) -> None:
        self.mnemonic = 'abuse boss fly battle rubber wasp afraid hamster guide essence vibrant tattoo'
        self.master_xprv = 'xprv9s21ZrQH143K25JhKqEwvJW7QAiVvkmi4WRenBZanA6kxHKtKAQQKwZG65kCyW5jWJ8NY9e3GkRoistUjjcpHNsGBUv94istDPXvqGNuWpC'

    def test_sha256(self):
        params = ParamsOfHash(
            data=base64.b64encode('TON is our future'.encode()).decode())
        result = async_core_client.crypto.sha256(params=params)
        self.assertEqual(
            '1e7fd5ec201652b5375e5edf3e86d0513394d2c2004dd506415abf0578261951',
            result.hash)

        params.data = base64.b64encode(
            bytes.fromhex('544f4e206973206f757220667574757265')).decode()
        result = async_core_client.crypto.sha256(params=params)
        self.assertEqual(
            '1e7fd5ec201652b5375e5edf3e86d0513394d2c2004dd506415abf0578261951',
            result.hash)

        params.data = 'VE9OIGlzIG91ciBmdXR1cmU='
        result = async_core_client.crypto.sha256(params=params)
        self.assertEqual(
            '1e7fd5ec201652b5375e5edf3e86d0513394d2c2004dd506415abf0578261951',
            result.hash)

    def test_sha512(self):
        data = base64.b64encode('TON is our future'.encode()).decode()
        params = ParamsOfHash(data=data)
        result = async_core_client.crypto.sha512(params=params)
        self.assertEqual(
            '4c52dd4cefc68319bac5e97c1f0d18ae8194fb0dd8d9e090ba8376834a0756175a9a736d1e69cb1a58d25c3d554b02a2b8ed9c3ae5cbeeccc3277746a363a434',
            result.hash)

    def test_hdkey_xprv_from_mnemonic(self):
        params = ParamsOfHDKeyXPrvFromMnemonic(phrase=self.mnemonic)
        result = async_core_client.crypto.hdkey_xprv_from_mnemonic(
            params=params)
        self.assertEqual(self.master_xprv, result.xprv)

        with self.assertRaises(TonException):
            params.phrase = 0
            async_core_client.crypto.hdkey_xprv_from_mnemonic(params=params)

    def test_hdkey_secret_from_xprv(self):
        params = ParamsOfHDKeySecretFromXPrv(xprv=self.master_xprv)
        result = async_core_client.crypto.hdkey_secret_from_xprv(params=params)
        self.assertEqual(
            '0c91e53128fa4d67589d63a6c44049c1068ec28a63069a55ca3de30c57f8b365',
            result.secret)

        with self.assertRaises(TonException):
            params.xprv = ''
            async_core_client.crypto.hdkey_secret_from_xprv(params=params)

    def test_hdkey_public_from_xprv(self):
        params = ParamsOfHDKeyPublicFromXPrv(xprv=self.master_xprv)
        result = async_core_client.crypto.hdkey_public_from_xprv(params=params)
        self.assertEqual(
            '7b70008d0c40992283d488b1046739cf827afeabf647a5f07c4ad1e7e45a6f89',
            result.public)

    def test_hdkey_derive_from_xprv(self):
        params = ParamsOfHDKeyDeriveFromXPrv(
            xprv=self.master_xprv, child_index=0, hardened=False)
        result = async_core_client.crypto.hdkey_derive_from_xprv(params=params)
        self.assertEqual(
            'xprv9uZwtSeoKf1swgAkVVCEUmC2at6t7MCJoHnBbn1MWJZyxQ4cySkVXPyNh7zjf9VjsP4vEHDDD2a6R35cHubg4WpzXRzniYiy8aJh1gNnBKv',
            result.xprv)

        with self.assertRaises(TonException):
            params.child_index = -1
            async_core_client.crypto.hdkey_derive_from_xprv(params=params)

    def test_hdkey_derive_from_xprv_path(self):
        params = ParamsOfHDKeyDeriveFromXPrvPath(
            xprv=self.master_xprv, path="m/44'/60'/0'/0'")
        result = async_core_client.crypto.hdkey_derive_from_xprv_path(
            params=params)
        self.assertEqual(
            'xprvA1KNMo63UcGjmDF1bX39Cw2BXGUwrwMjeD5qvQ3tA3qS3mZQkGtpf4DHq8FDLKAvAjXsYGLHDP2dVzLu9ycta8PXLuSYib2T3vzLf3brVgZ',
            result.xprv)

        with self.assertRaises(TonException):
            params.path = 'm/'
            async_core_client.crypto.hdkey_derive_from_xprv_path(params=params)

    def test_convert_public_key_to_ton_safe_format(self):
        params = ParamsOfConvertPublicKeyToTonSafeFormat(
            public_key='06117f59ade83e097e0fb33e5d29e8735bda82b3bf78a015542aaa853bb69600')
        safe = async_core_client.crypto.convert_public_key_to_ton_safe_format(
            params=params)
        self.assertEqual(
            'PuYGEX9Zreg-CX4Psz5dKehzW9qCs794oBVUKqqFO7aWAOTD',
            safe.ton_public_key)

        with self.assertRaises(TonException):
            params.public_key = None
            async_core_client.crypto.convert_public_key_to_ton_safe_format(
                params=params)

    def test_generate_random_sign_keys(self):
        keypair = async_core_client.crypto.generate_random_sign_keys()
        self.assertEqual(64, len(keypair.public))
        self.assertEqual(64, len(keypair.secret))
        self.assertNotEqual(keypair.secret, keypair.public)

    def test_sign_and_verify(self):
        unsigned = base64.b64encode('Test Message'.encode()).decode()
        keypair = KeyPair(
            public='1869b7ef29d58026217e9cf163cbfbd0de889bdf1bf4daebf5433a312f5b8d6e',
            secret='56b6a77093d6fdf14e593f36275d872d75de5b341942376b2a08759f3cbae78f')

        # Sign message
        sign_params = ParamsOfSign(unsigned=unsigned, keys=keypair)
        signed = async_core_client.crypto.sign(params=sign_params)
        self.assertEqual(
            '+wz+QO6l1slgZS5s65BNqKcu4vz24FCJz4NSAxef9lu0jFfs8x3PzSZRC+pn5k8+aJi3xYMA3BQzglQmjK3hA1Rlc3QgTWVzc2FnZQ==',
            signed.signed)
        self.assertEqual(
            'fb0cfe40eea5d6c960652e6ceb904da8a72ee2fcf6e05089cf835203179ff65bb48c57ecf31dcfcd26510bea67e64f3e6898b7c58300dc14338254268cade103',
            signed.signature)

        # Verify signature
        verify_params = ParamsOfVerifySignature(
            signed=signed.signed, public=keypair.public)
        verified = async_core_client.crypto.verify_signature(
            params=verify_params)
        self.assertEqual(unsigned, verified.unsigned)
        self.assertEqual(
            base64.b64decode(unsigned.encode()),
            base64.b64decode(verified.unsigned.encode()))

        with self.assertRaises(TonException):
            sign_params.keys = KeyPair(public='1', secret='2')
            async_core_client.crypto.sign(params=sign_params)

        with self.assertRaises(TonException):
            verify_params.signed = 'simple'
            async_core_client.crypto.verify_signature(params=verify_params)

    def test_modular_power(self):
        params = ParamsOfModularPower(
            base='0123456789ABCDEF', exponent='0123', modulus='01234567')
        result = async_core_client.crypto.modular_power(params=params)
        self.assertEqual('63bfdf', result.modular_power)

        with self.assertRaises(TonException):
            params.base = '1'
            params.modulus = '0.2'
            async_core_client.crypto.modular_power(params=params)

    def test_factorize(self):
        params = ParamsOfFactorize(composite='17ED48941A08F981')
        result = async_core_client.crypto.factorize(params=params)
        self.assertIsInstance(result.factors, list)
        self.assertEqual('494C553B', result.factors[0])
        self.assertEqual('53911073', result.factors[1])

        with self.assertRaises(TonException):
            params.composite = 'a3'
            async_core_client.crypto.factorize(params=params)

    def test_ton_crc16(self):
        params = ParamsOfTonCrc16(
            data=base64.b64encode(bytes.fromhex('0123456789abcdef')).decode())
        result = async_core_client.crypto.ton_crc16(params=params)
        self.assertEqual(43349, result.crc)

        with self.assertRaises(TonException):
            params.data = '0=='
            async_core_client.crypto.ton_crc16(params=params)

    def test_generate_random_bytes(self):
        params = ParamsOfGenerateRandomBytes(length=32)
        result = async_core_client.crypto.generate_random_bytes(params=params)
        self.assertEqual(44, len(result.bytes))
        bts = base64.b64decode(result.bytes.encode())
        self.assertEqual(32, len(bts))

        with self.assertRaises(TonException):
            params.length = '1'
            async_core_client.crypto.generate_random_bytes(params=params)

    def test_mnemonic_words(self):
        params = ParamsOfMnemonicWords()
        result = async_core_client.crypto.mnemonic_words(params=params)
        self.assertEqual(2048, len(result.words.split(' ')))

        with self.assertRaises(TonException):
            params.dictionary = 100
            async_core_client.crypto.mnemonic_words(params=params)

    def test_mnemonic_from_random(self):
        params = ParamsOfMnemonicFromRandom()
        result = async_core_client.crypto.mnemonic_from_random(params=params)
        self.assertEqual(12, len(result.phrase.split(' ')))

        for d in range(1, 8):
            for count in [12, 15, 18, 21, 24]:
                params.dictionary = list(MnemonicDictionary)[d]
                params.word_count = count
                result = async_core_client.crypto.mnemonic_from_random(
                    params=params)
                self.assertEqual(count, len(result.phrase.split(' ')))

        with self.assertRaises(TonException):
            params.word_count = 0
            async_core_client.crypto.mnemonic_from_random(params=params)

    def test_mnemonic_from_entropy(self):
        params = ParamsOfMnemonicFromEntropy(
            entropy='00112233445566778899AABBCCDDEEFF')
        result = async_core_client.crypto.mnemonic_from_entropy(params=params)
        self.assertEqual(
            'abandon math mimic master filter design carbon crystal rookie group knife young',
            result.phrase)

        with self.assertRaises(TonException):
            params.entropy = '01'
            async_core_client.crypto.mnemonic_from_entropy(params=params)

    def test_mnemonic_verify(self):
        m_params = ParamsOfMnemonicFromRandom()
        result = async_core_client.crypto.mnemonic_from_random(params=m_params)

        v_params = ParamsOfMnemonicVerify(phrase=result.phrase)
        result = async_core_client.crypto.mnemonic_verify(params=v_params)
        self.assertEqual(True, result.valid)

        for d in range(1, 8):
            for count in [12, 15, 18, 21, 24]:
                m_params.dictionary = list(MnemonicDictionary)[d]
                m_params.word_count = count
                mnemonic = async_core_client.crypto.mnemonic_from_random(
                    params=m_params)

                v_params.phrase = mnemonic.phrase
                v_params.dictionary = m_params.dictionary
                v_params.word_count = m_params.word_count
                result = async_core_client.crypto.mnemonic_verify(
                    params=v_params)
                self.assertEqual(True, result.valid)

        v_params = ParamsOfMnemonicVerify(phrase='one')
        result = async_core_client.crypto.mnemonic_verify(params=v_params)
        self.assertEqual(False, result.valid)

    def test_mnemonic_derive_sign_keys(self):
        # Derive from random phrase
        params = ParamsOfMnemonicFromRandom()
        mnemonic = async_core_client.crypto.mnemonic_from_random(params=params)

        params = ParamsOfMnemonicDeriveSignKeys(phrase=mnemonic.phrase)
        keypair = async_core_client.crypto.mnemonic_derive_sign_keys(
            params=params)
        self.assertIsInstance(keypair, KeyPair)

        # Derive from provided phrase and convert public to ton_safe
        phrase = 'unit follow zone decline glare flower crisp vocal adapt magic much mesh cherry teach mechanic rain float vicious solution assume hedgehog rail sort chuckle'
        derive_params = ParamsOfMnemonicDeriveSignKeys(
            phrase=phrase, dictionary=MnemonicDictionary.TON, word_count=24)
        keypair = async_core_client.crypto.mnemonic_derive_sign_keys(
            params=derive_params)

        convert_params = ParamsOfConvertPublicKeyToTonSafeFormat(
            public_key=keypair.public)
        result = async_core_client.crypto.convert_public_key_to_ton_safe_format(
            params=convert_params)
        self.assertEqual(
            'PuYTvCuf__YXhp-4jv3TXTHL0iK65ImwxG0RGrYc1sP3H4KS',
            result.ton_public_key)

        # Derive with path
        derive_params = ParamsOfMnemonicDeriveSignKeys(
            phrase=phrase, path='m', dictionary=MnemonicDictionary.TON,
            word_count=24)
        keypair = async_core_client.crypto.mnemonic_derive_sign_keys(
            params=derive_params)

        convert_params = ParamsOfConvertPublicKeyToTonSafeFormat(
            public_key=keypair.public)
        result = async_core_client.crypto.convert_public_key_to_ton_safe_format(
            params=convert_params)
        self.assertEqual(
            'PubDdJkMyss2qHywFuVP1vzww0TpsLxnRNnbifTCcu-XEgW0',
            result.ton_public_key)

        # Derive from 12-word phrase
        phrase = 'abandon math mimic master filter design carbon crystal rookie group knife young'
        derive_params = ParamsOfMnemonicDeriveSignKeys(phrase=phrase)
        keypair = async_core_client.crypto.mnemonic_derive_sign_keys(
            params=derive_params)

        convert_params = ParamsOfConvertPublicKeyToTonSafeFormat(
            public_key=keypair.public)
        result = async_core_client.crypto.convert_public_key_to_ton_safe_format(
            params=convert_params)
        self.assertEqual(
            'PuZhw8W5ejPJwKA68RL7sn4_RNmeH4BIU_mEK7em5d4_-cIx',
            result.ton_public_key)

        # Derive from mnemonic from entropy
        params = ParamsOfMnemonicFromEntropy(
            entropy='2199ebe996f14d9e4e2595113ad1e627')
        mnemonic = async_core_client.crypto.mnemonic_from_entropy(
            params=params)

        derive_params = ParamsOfMnemonicDeriveSignKeys(phrase=mnemonic.phrase)
        keypair = async_core_client.crypto.mnemonic_derive_sign_keys(
            params=derive_params)

        convert_params = ParamsOfConvertPublicKeyToTonSafeFormat(
            public_key=keypair.public)
        result = async_core_client.crypto.convert_public_key_to_ton_safe_format(
            params=convert_params)
        self.assertEqual(
            'PuZdw_KyXIzo8IksTrERN3_WoAoYTyK7OvM-yaLk711sUIB3',
            result.ton_public_key)

    def test_nacl_sign_keypair_from_secret_key(self):
        params = ParamsOfNaclSignKeyPairFromSecret(
            secret='8fb4f2d256e57138fb310b0a6dac5bbc4bee09eb4821223a720e5b8e1f3dd674')
        keypair = async_core_client.crypto.nacl_sign_keypair_from_secret_key(
            params=params)
        self.assertEqual(
            'aa5533618573860a7e1bf19f34bd292871710ed5b2eafa0dcdbb33405f2231c6',
            keypair.public)

        with self.assertRaises(TonException):
            params.secret = '0a'
            async_core_client.crypto.nacl_sign_keypair_from_secret_key(
                params=params)

    def test_nacl_sign(self):
        # Nacl sign data
        unsigned = base64.b64encode('Test Message'.encode()).decode()
        secret = '56b6a77093d6fdf14e593f36275d872d75de5b341942376b2a08759f3cbae78f1869b7ef29d58026217e9cf163cbfbd0de889bdf1bf4daebf5433a312f5b8d6e'

        params = ParamsOfNaclSign(unsigned=unsigned, secret=secret)
        signed = async_core_client.crypto.nacl_sign(params=params)
        self.assertEqual(
            '+wz+QO6l1slgZS5s65BNqKcu4vz24FCJz4NSAxef9lu0jFfs8x3PzSZRC+pn5k8+aJi3xYMA3BQzglQmjK3hA1Rlc3QgTWVzc2FnZQ==',
            signed.signed)

        # Nacl sign open
        params = ParamsOfNaclSignOpen(
            signed=signed.signed,
            public='1869b7ef29d58026217e9cf163cbfbd0de889bdf1bf4daebf5433a312f5b8d6e')
        result = async_core_client.crypto.nacl_sign_open(params=params)
        self.assertEqual(unsigned, result.unsigned)

        # Nacl sign detached
        params = ParamsOfNaclSign(unsigned=unsigned, secret=secret)
        result = async_core_client.crypto.nacl_sign_detached(params=params)
        self.assertEqual(
            'fb0cfe40eea5d6c960652e6ceb904da8a72ee2fcf6e05089cf835203179ff65bb48c57ecf31dcfcd26510bea67e64f3e6898b7c58300dc14338254268cade103',
            result.signature)

        # Nacl sign detached verify signature
        params = ParamsOfNaclSignDetachedVerify(
            unsigned=unsigned, signature=result.signature,
            public='1869b7ef29d58026217e9cf163cbfbd0de889bdf1bf4daebf5433a312f5b8d6e')
        result = async_core_client.crypto.nacl_sign_detached_verify(
            params=params)
        self.assertEqual(True, result.succeeded)

        with self.assertRaises(TonException):
            params.secret = '0=='
            async_core_client.crypto.nacl_sign(params=params)

        with self.assertRaises(TonException):
            params = ParamsOfNaclSignOpen(signed=signed.signed, public='0x00')
            async_core_client.crypto.nacl_sign_open(params=params)

        with self.assertRaises(TonException):
            params = ParamsOfNaclSign(unsigned='100', secret=secret)
            params.unsigned = 100
            async_core_client.crypto.nacl_sign_detached(params=params)

    def test_nacl_box_keypair(self):
        keypair = async_core_client.crypto.nacl_box_keypair()
        self.assertEqual(64, len(keypair.public))
        self.assertEqual(64, len(keypair.secret))
        self.assertNotEqual(keypair.public, keypair.secret)

    def test_nacl_box_keypair_from_secret_key(self):
        params = ParamsOfNaclBoxKeyPairFromSecret(
            secret='e207b5966fb2c5be1b71ed94ea813202706ab84253bdf4dc55232f82a1caf0d4')
        keypair = async_core_client.crypto.nacl_box_keypair_from_secret_key(
            params=params)
        self.assertEqual(
            'a53b003d3ffc1e159355cb37332d67fc235a7feb6381e36c803274074dc3933a',
            keypair.public)

        with self.assertRaises(TonException):
            params.secret = '0x00'
            async_core_client.crypto.nacl_box_keypair_from_secret_key(
                params=params)

    def test_nacl_box_and_open(self):
        decrypted = base64.b64encode('Test Message'.encode()).decode()
        nonce = 'cd7f99924bf422544046e83595dd5803f17536f5c9a11746'
        their_public = 'c4e2d9fe6a6baf8d1812b799856ef2a306291be7a7024837ad33a8530db79c6b'
        secret = 'd9b9dc5033fb416134e5d2107fdbacab5aadb297cb82dbdcd137d663bac59f7f'

        # Create nacl box
        box_params = ParamsOfNaclBox(
            decrypted=decrypted, nonce=nonce, their_public=their_public,
            secret=secret)
        box = async_core_client.crypto.nacl_box(params=box_params)
        self.assertEqual(
            'li4XED4kx/pjQ2qdP0eR2d/K30uN94voNADxwA==', box.encrypted)

        # Open nacl box
        box_open_params = ParamsOfNaclBoxOpen(
            encrypted=box.encrypted, nonce=nonce, their_public=their_public,
            secret=secret)
        opened = async_core_client.crypto.nacl_box_open(params=box_open_params)
        self.assertEqual(decrypted, opened.decrypted)

        with self.assertRaises(TonException):
            box_params.decrypted = '0x00'
            box_params.their_public = ''
            async_core_client.crypto.nacl_box(params=box_params)

        with self.assertRaises(TonException):
            box_open_params.secret = ''
            async_core_client.crypto.nacl_box_open(params=box_open_params)

    def test_nacl_secret_box_and_open(self):
        decrypted = base64.b64encode(
            'Test Message \' \" {} $=,?'.encode()).decode()
        nonce = '2a33564717595ebe53d91a785b9e068aba625c8453a76e45'
        key = '8f68445b4e78c000fe4d6b7fc826879c1e63e3118379219a754ae66327764bd8'

        # Create nacl secret box
        box_params = ParamsOfNaclSecretBox(
            decrypted=decrypted, nonce=nonce, key=key)
        box = async_core_client.crypto.nacl_secret_box(params=box_params)
        self.assertEqual(
            'I6QZteixTdul0K0ldT+/U4QF0t/C1Q8RGyzQ2Hl7886DpW3/DK5ijg==',
            box.encrypted)

        # Open nacl secret box
        box_open_params = ParamsOfNaclSecretBoxOpen(
            encrypted=box.encrypted, nonce=nonce, key=key)
        opened = async_core_client.crypto.nacl_secret_box_open(
            params=box_open_params)
        self.assertEqual(decrypted, opened.decrypted)

        with self.assertRaises(TonException):
            box_params.decrypted = '0x00'
            box_params.key = None
            async_core_client.crypto.nacl_secret_box(params=box_params)

        with self.assertRaises(TonException):
            box_open_params.key = ''
            async_core_client.crypto.nacl_secret_box_open(
                params=box_open_params)

    def test_scrypt(self):
        password = base64.b64encode('Test Password'.encode()).decode()
        salt = base64.b64encode('Test Salt'.encode()).decode()

        params = ParamsOfScrypt(
            password=password, salt=salt, log_n=10, r=8, p=16, dk_len=64)
        result = async_core_client.crypto.scrypt(params=params)
        self.assertEqual(
            '52e7fcf91356eca55fc5d52f16f5d777e3521f54e3c570c9bbb7df58fc15add73994e5db42be368de7ebed93c9d4f21f9be7cc453358d734b04a057d0ed3626d',
            result.key)

        with self.assertRaises(TonException):
            params.dk_len = 0
            async_core_client.crypto.scrypt(params=params)

    def test_chacha20(self):
        key = '01' * 32
        nonce = 'ff' * 12
        data = base64.b64encode(b'Message').decode()

        params = ParamsOfChaCha20(data=data, key=key, nonce=nonce)
        encrypted = async_core_client.crypto.chacha20(params=params)
        self.assertEqual('w5QOGsJodQ==', encrypted.data)

        params.data = encrypted.data
        decrypted = async_core_client.crypto.chacha20(params=params)
        self.assertEqual(data, decrypted.data)

    def test_signing_box(self):
        keypair = async_core_client.crypto.generate_random_sign_keys()

        # Create handle
        signing_box = async_core_client.crypto.get_signing_box(params=keypair)
        self.assertIsInstance(signing_box.handle, int)

        # Get public key from box
        result = async_core_client.crypto.signing_box_get_public_key(
            params=signing_box)
        self.assertEqual(keypair.public, result.pubkey)

        # Sign with box
        message = base64.b64encode(b'Sign with box').decode()

        params = ParamsOfSigningBoxSign(
            signing_box=signing_box.handle, unsigned=message)
        box_result = async_core_client.crypto.signing_box_sign(params=params)

        sign_params = ParamsOfSign(unsigned=message, keys=keypair)
        sign_result = async_core_client.crypto.sign(params=sign_params)
        self.assertEqual(sign_result.signature, box_result.signature)

        # Remove signing box
        async_core_client.crypto.remove_signing_box(params=signing_box)

    def test_register_signing_box(self):
        from concurrent.futures import ThreadPoolExecutor
        keys = async_core_client.crypto.generate_random_sign_keys()
        keys_box_handle = async_core_client.crypto.get_signing_box(params=keys)

        def __callback(response_data, *args):
            request = ParamsOfAppRequest(**response_data)
            box_params = ParamsOfAppSigningBox.from_dict(
                data=request.request_data)
            box_result = None

            if isinstance(box_params, ParamsOfAppSigningBox.GetPublicKey):
                # Run method and wait for result
                with ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        async_core_client.crypto.signing_box_get_public_key,
                        params=keys_box_handle)
                    _result = future.result()

                # Resolve params
                box_result = ResultOfAppSigningBox.GetPublicKey(
                    public_key=_result.pubkey)
            if isinstance(box_params, ParamsOfAppSigningBox.Sign):
                # Run method and wait for result
                params = ParamsOfSigningBoxSign(
                    signing_box=keys_box_handle.handle,
                    unsigned=box_params.unsigned)
                with ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        async_core_client.crypto.signing_box_sign,
                        params=params)
                    _result = future.result()

                # Resolve params
                box_result = ResultOfAppSigningBox.Sign(
                    signature=_result.signature)

            # Create resolve app request params
            request_result = AppRequestResult.Ok(
                result=box_result.dict)
            resolve_params = ParamsOfResolveAppRequest(
                app_request_id=request.app_request_id,
                result=request_result)
            with ThreadPoolExecutor() as executor:
                future = executor.submit(
                    async_core_client.resolve_app_request,
                    params=resolve_params)
                future.result()

        # Get external signing box
        external_box = async_core_client.crypto.register_signing_box(
            callback=__callback)

        # Request box public key
        box_pubkey = async_core_client.crypto.signing_box_get_public_key(
            params=external_box)
        self.assertEqual(keys.public, box_pubkey.pubkey)

        # Get signature from signing box
        unsigned = base64.b64encode(b'Test Message').decode()
        sign_params = ParamsOfSigningBoxSign(
            signing_box=external_box.handle, unsigned=unsigned)
        box_sign = async_core_client.crypto.signing_box_sign(
            params=sign_params)

        # Get signature by keys
        sign_params = ParamsOfSign(unsigned=unsigned, keys=keys)
        keys_sign = async_core_client.crypto.sign(params=sign_params)

        self.assertEqual(keys_sign.signature, box_sign.signature)

        async_core_client.crypto.remove_signing_box(params=external_box)

    def test_encryption_box(self):
        from concurrent.futures import ThreadPoolExecutor

        def __callback(response_data, *args):
            request = ParamsOfAppRequest(**response_data)
            box_params = ParamsOfAppEncryptionBox.from_dict(
                data=request.request_data)
            box_result = None

            if isinstance(box_params, ParamsOfAppEncryptionBox.GetInfo):
                _info = EncryptionBoxInfo(algorithm='duplicator')
                box_result = ResultOfAppEncryptionBox.GetInfo(info=_info)
            if isinstance(box_params, ParamsOfAppEncryptionBox.Encrypt):
                data = box_params.data * 2
                box_result = ResultOfAppEncryptionBox.Encrypt(data=data)
            if isinstance(box_params, ParamsOfAppEncryptionBox.Decrypt):
                end = int(len(box_params.data) / 2)
                data = box_params.data[:end]
                box_result = ResultOfAppEncryptionBox.Decrypt(data=data)

            # Create resolve app request params
            request_result = AppRequestResult.Ok(
                result=box_result.dict)
            resolve_params = ParamsOfResolveAppRequest(
                app_request_id=request.app_request_id,
                result=request_result)
            with ThreadPoolExecutor() as executor:
                future = executor.submit(
                    async_core_client.resolve_app_request,
                    params=resolve_params)
                future.result()

        # Register box
        box = async_core_client.crypto.register_encryption_box(
            callback=__callback)

        # Get info
        info_result = async_core_client.crypto.encryption_box_get_info(
            params=ParamsOfEncryptionBoxGetInfo(encryption_box=box.handle))
        self.assertEqual(info_result.info.algorithm, 'duplicator')

        # Encrypt
        enc_data = '12345'
        params = ParamsOfEncryptionBoxEncrypt(
            encryption_box=box.handle, data=enc_data)
        enc_result = async_core_client.crypto.encryption_box_encrypt(
            params=params)
        self.assertEqual(enc_data * 2, enc_result.data)

        # Decrypt
        params = ParamsOfEncryptionBoxDecrypt(
            encryption_box=box.handle, data=enc_result.data)
        dec_result = async_core_client.crypto.encryption_box_decrypt(
            params=params)
        self.assertEqual(enc_data, dec_result.data)

        # Remove box
        async_core_client.crypto.remove_encryption_box(params=box)


class TestTonCryptoSyncCore(unittest.TestCase):
    """ Sync core is not recommended to use, so make just a couple of tests """
    def test_sha256(self):
        data = base64.b64encode('TON is our future'.encode()).decode()
        params = ParamsOfHash(data=data)
        result = sync_core_client.crypto.sha256(params=params)
        self.assertEqual(
            '1e7fd5ec201652b5375e5edf3e86d0513394d2c2004dd506415abf0578261951',
            result.hash)

        data = base64.b64encode(
            bytes.fromhex('544f4e206973206f757220667574757265')).decode()
        params.data = data
        result = sync_core_client.crypto.sha256(params=params)
        self.assertEqual(
            '1e7fd5ec201652b5375e5edf3e86d0513394d2c2004dd506415abf0578261951',
            result.hash)

        data = 'VE9OIGlzIG91ciBmdXR1cmU='
        params.data = data
        result = sync_core_client.crypto.sha256(params=params)
        self.assertEqual(
            '1e7fd5ec201652b5375e5edf3e86d0513394d2c2004dd506415abf0578261951',
            result.hash)

    def test_sha512(self):
        data = base64.b64encode('TON is our future'.encode()).decode()
        params = ParamsOfHash(data=data)
        result = sync_core_client.crypto.sha512(params=params)
        self.assertEqual(
            '4c52dd4cefc68319bac5e97c1f0d18ae8194fb0dd8d9e090ba8376834a0756175a9a736d1e69cb1a58d25c3d554b02a2b8ed9c3ae5cbeeccc3277746a363a434',
            result.hash)

    def test_scrypt(self):
        password = base64.b64encode('Test Password'.encode()).decode()
        salt = base64.b64encode('Test Salt'.encode()).decode()

        params = ParamsOfScrypt(
            password=password, salt=salt, log_n=10, r=8, p=16, dk_len=64)
        result = sync_core_client.crypto.scrypt(params=params)
        self.assertEqual(
            '52e7fcf91356eca55fc5d52f16f5d777e3521f54e3c570c9bbb7df58fc15add73994e5db42be368de7ebed93c9d4f21f9be7cc453358d734b04a057d0ed3626d',
            result.key)

        with self.assertRaises(TonException):
            params.dk_len = 0
            sync_core_client.crypto.scrypt(params=params)
