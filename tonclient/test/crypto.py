import json
import unittest
import base64
from io import StringIO

from tonclient.client import TonClient, DEVNET_BASE_URL
from tonclient.types import KeyPair, MnemonicDictionary
from tonclient.errors import TonException

client = TonClient(network={'server_address': DEVNET_BASE_URL}, is_async=False)


class TestKeyPairType(unittest.TestCase):
    def setUp(self) -> None:
        self.keypair = KeyPair(
            public="2e750ea795aad6e04ae1544132619c6a5e1356c36db60532320dae6aa656cf2e",
            secret="7ee962326304f9f88d5048fabdde7921411b1aad6400ef984c85a0a9cb3b1a7c")

    def test_load_io(self):
        stream = StringIO()
        stream.write(json.dumps(self.keypair.dict))
        keypair = KeyPair.load_io(io=stream)
        self.assertIsInstance(keypair, KeyPair)
        self.assertEqual(keypair.secret, self.keypair.secret)
        stream.close()

        stream = StringIO()
        stream.write(self.keypair.binary.hex())
        keypair = KeyPair.load_io(io=stream, as_binary=True)
        self.assertIsInstance(keypair, KeyPair)
        self.assertEqual(keypair.public, self.keypair.public)
        stream.close()

    def test_dump_io(self):
        stream = StringIO()
        self.keypair.dump_io(io=stream)
        self.assertEqual(stream.getvalue(), json.dumps(self.keypair.dict))
        stream.close()

        stream = StringIO()
        self.keypair.dump_io(io=stream, as_binary=True)
        self.assertEqual(bytes.fromhex(stream.getvalue()), self.keypair.binary)
        stream.close()


class TestTonCrypto(unittest.TestCase):
    def setUp(self) -> None:
        self.mnemonic = 'abuse boss fly battle rubber wasp afraid hamster guide essence vibrant tattoo'
        self.master_xprv = 'xprv9s21ZrQH143K25JhKqEwvJW7QAiVvkmi4WRenBZanA6kxHKtKAQQKwZG65kCyW5jWJ8NY9e3GkRoistUjjcpHNsGBUv94istDPXvqGNuWpC'

    def test_sha256(self):
        data = base64.b64encode('Message to hash with sha 256'.encode())
        result = client.crypto.sha256(data=data)
        self.assertEqual(
            '16fd057308dd358d5a9b3ba2de766b2dfd5e308478fc1f7ba5988db2493852f5',
            result)

        data = base64.b64encode(bytes.fromhex(
            '4d65737361676520746f206861736820776974682073686120323536'))
        result = client.crypto.sha256(data=data)
        self.assertEqual(
            '16fd057308dd358d5a9b3ba2de766b2dfd5e308478fc1f7ba5988db2493852f5',
            result)

        result = client.crypto.sha256(
            data='TWVzc2FnZSB0byBoYXNoIHdpdGggc2hhIDI1Ng==')
        self.assertEqual(
            '16fd057308dd358d5a9b3ba2de766b2dfd5e308478fc1f7ba5988db2493852f5',
            result)

    def test_sha512(self):
        data = base64.b64encode('Message to hash with sha 512'.encode())
        result = client.crypto.sha512(data=data)
        self.assertEqual(
            '2616a44e0da827f0244e93c2b0b914223737a6129bc938b8edf2780ac9482960baa9b7c7cdb11457c1cebd5ae77e295ed94577f32d4c963dc35482991442daa5',
            result)

    def test_hdkey_xprv_from_mnemonic(self):
        xprv = client.crypto.hdkey_xprv_from_mnemonic(phrase=self.mnemonic)
        self.assertEqual(self.master_xprv, xprv)

        with self.assertRaises(TonException):
            client.crypto.hdkey_xprv_from_mnemonic(phrase=0)

    def test_hdkey_secret_from_xprv(self):
        secret = client.crypto.hdkey_secret_from_xprv(xprv=self.master_xprv)
        self.assertEqual(
            '0c91e53128fa4d67589d63a6c44049c1068ec28a63069a55ca3de30c57f8b365',
            secret)

        with self.assertRaises(TonException):
            client.crypto.hdkey_secret_from_xprv(xprv='')

    def test_hdkey_public_from_xprv(self):
        public = client.crypto.hdkey_public_from_xprv(xprv=self.master_xprv)
        self.assertEqual(
            '02a8eb63085f73c33fa31b4d1134259406347284f8dab6fc68f4bf8c96f6c39b75',
            public)

    def test_hdkey_derive_from_xprv(self):
        child_xprv = client.crypto.hdkey_derive_from_xprv(
            xprv=self.master_xprv, child_index=0, hardened=False)
        self.assertEqual(
            'xprv9uZwtSeoKf1swgAkVVCEUmC2at6t7MCJoHnBbn1MWJZyxQ4cySkVXPyNh7zjf9VjsP4vEHDDD2a6R35cHubg4WpzXRzniYiy8aJh1gNnBKv',
            child_xprv)

        with self.assertRaises(TonException):
            client.crypto.hdkey_derive_from_xprv(
                xprv=self.master_xprv, child_index=-1, hardened=False)

        secret = client.crypto.hdkey_secret_from_xprv(xprv=child_xprv)
        self.assertEqual(
            '518afc6489b61d4b738ee9ad9092815fa014ffa6e9a280fa17f84d95f31adb91',
            secret)

        public = client.crypto.hdkey_public_from_xprv(xprv=child_xprv)
        self.assertEqual(
            '027a598c7572dbb4fbb9663a0c805576babf7faa173a4288a48a52f6f427e12be1',
            public)

    def test_hdkey_derive_from_xprv_path(self):
        child = client.crypto.hdkey_derive_from_xprv_path(
            xprv=self.master_xprv, path="m/44'/60'/0'/0'")
        self.assertEqual(
            'xprvA1KNMo63UcGjmDF1bX39Cw2BXGUwrwMjeD5qvQ3tA3qS3mZQkGtpf4DHq8FDLKAvAjXsYGLHDP2dVzLu9ycta8PXLuSYib2T3vzLf3brVgZ',
            child)

        with self.assertRaises(TonException):
            client.crypto.hdkey_derive_from_xprv_path(
                xprv=self.master_xprv, path='m/')

        secret = client.crypto.hdkey_secret_from_xprv(xprv=child)
        self.assertEqual(
            '1c566ade41169763b155761406d3cef08b29b31cf8014f51be08c0cb4e67c5e1',
            secret)

        public = client.crypto.hdkey_public_from_xprv(xprv=child)
        self.assertEqual(
            '02a87d9764eedaacee45b0f777b5a242939b05fa06873bf511ca9a59cb46a5f526',
            public)

    def test_convert_public_key_to_ton_safe_format(self):
        safe = client.crypto.convert_public_key_to_ton_safe_format(
            public_key='06117f59ade83e097e0fb33e5d29e8735bda82b3bf78a015542aaa853bb69600')
        self.assertEqual(
            'PuYGEX9Zreg-CX4Psz5dKehzW9qCs794oBVUKqqFO7aWAOTD', safe)

        with self.assertRaises(TonException):
            client.crypto.convert_public_key_to_ton_safe_format(
                public_key=None)

    def test_generate_random_sign_keys(self):
        keypair = client.crypto.generate_random_sign_keys()
        self.assertEqual(64, len(keypair.public))
        self.assertEqual(64, len(keypair.secret))
        self.assertNotEqual(keypair.secret, keypair.public)

    def test_sign_and_verify(self):
        unsigned = base64.b64encode('Test Message'.encode())
        keypair = KeyPair(
            public='1869b7ef29d58026217e9cf163cbfbd0de889bdf1bf4daebf5433a312f5b8d6e',
            secret='56b6a77093d6fdf14e593f36275d872d75de5b341942376b2a08759f3cbae78f')

        # Sign message
        signed = client.crypto.sign(unsigned=unsigned, keys=keypair)
        self.assertEqual(
            '+wz+QO6l1slgZS5s65BNqKcu4vz24FCJz4NSAxef9lu0jFfs8x3PzSZRC+pn5k8+aJi3xYMA3BQzglQmjK3hA1Rlc3QgTWVzc2FnZQ==',
            signed['signed'])
        self.assertEqual(
            'fb0cfe40eea5d6c960652e6ceb904da8a72ee2fcf6e05089cf835203179ff65bb48c57ecf31dcfcd26510bea67e64f3e6898b7c58300dc14338254268cade103',
            signed['signature'])

        # Verify signature
        verified = client.crypto.verify_signature(
            signed=signed['signed'], public=keypair.public)
        self.assertEqual(unsigned.decode(), verified)
        self.assertEqual(
            base64.b64decode(unsigned), base64.b64decode(verified.encode()))

        with self.assertRaises(TonException):
            client.crypto.sign(
                unsigned=unsigned, keys=KeyPair(public='1', secret='2'))

        with self.assertRaises(TonException):
            client.crypto.verify_signature(
                signed='simple', public=keypair.public)

    def test_modular_power(self):
        result = client.crypto.modular_power(
            base='0123456789ABCDEF', exponent='0123', modulus='01234567')
        self.assertEqual('63bfdf', result)

        with self.assertRaises(TonException):
            client.crypto.modular_power(
                base='1', exponent='0123', modulus='0.2')

    def test_factorize(self):
        factors = client.crypto.factorize(composite='17ED48941A08F981')
        self.assertIsInstance(factors, list)
        self.assertEqual('494C553B', factors[0])
        self.assertEqual('53911073', factors[1])

        with self.assertRaises(TonException):
            client.crypto.factorize(composite='a3')

    def test_ton_crc16(self):
        data = base64.b64encode(bytes.fromhex('0123456789abcdef'))
        crc = client.crypto.ton_crc16(data=data)
        self.assertEqual(43349, crc)

        with self.assertRaises(TonException):
            client.crypto.ton_crc16(data='0==')

    def test_generate_random_bytes(self):
        bytes_b64 = client.crypto.generate_random_bytes(length=32)
        self.assertEqual(44, len(bytes_b64))
        bts = base64.b64decode(bytes_b64.encode())
        self.assertEqual(32, len(bts))

        with self.assertRaises(TonException):
            client.crypto.generate_random_bytes(length='1')

    def test_mnemonic_words(self):
        words = client.crypto.mnemonic_words()
        self.assertEqual(2048, len(words.split(' ')))

        with self.assertRaises(TonException):
            client.crypto.mnemonic_words(dictionary=100)

    def test_mnemonic_from_random(self):
        for count in [12, 15, 18, 21, 24]:
            mnemonic = client.crypto.mnemonic_from_random(word_count=count)
            self.assertEqual(count, len(mnemonic.split(' ')))

        with self.assertRaises(TonException):
            client.crypto.mnemonic_from_random(word_count=0)

    def test_mnemonic_from_entropy(self):
        mnemonic = client.crypto.mnemonic_from_entropy(
            entropy='00112233445566778899AABBCCDDEEFF')
        self.assertEqual(
            'abandon math mimic master filter design carbon crystal rookie group knife young',
            mnemonic)

        with self.assertRaises(TonException):
            client.crypto.mnemonic_from_entropy(entropy='01')

    def test_mnemonic_verify(self):
        for count in [12, 15, 18, 21, 24]:
            mnemonic = client.crypto.mnemonic_from_random(word_count=count)
            valid = client.crypto.mnemonic_verify(
                phrase=mnemonic, word_count=count)
            self.assertEqual(True, valid)

        valid = client.crypto.mnemonic_verify(phrase='one')
        self.assertEqual(False, valid)

    def test_mnemonic_derive_sign_keys(self):
        phrase = 'unit follow zone decline glare flower crisp vocal adapt magic much mesh cherry teach mechanic rain float vicious solution assume hedgehog rail sort chuckle'
        keypair = client.crypto.mnemonic_derive_sign_keys(
            phrase=phrase, dictionary=MnemonicDictionary.TON, word_count=24)
        public_safe = client.crypto.convert_public_key_to_ton_safe_format(
            public_key=keypair.public)
        self.assertEqual(
            'PuYTvCuf__YXhp-4jv3TXTHL0iK65ImwxG0RGrYc1sP3H4KS', public_safe)

        keypair = client.crypto.mnemonic_derive_sign_keys(
            phrase=phrase, path='m', dictionary=MnemonicDictionary.TON,
            word_count=24)
        public_safe = client.crypto.convert_public_key_to_ton_safe_format(
            public_key=keypair.public)
        self.assertEqual(
            'PubDdJkMyss2qHywFuVP1vzww0TpsLxnRNnbifTCcu-XEgW0', public_safe)

        phrase = 'abandon math mimic master filter design carbon crystal rookie group knife young'
        keypair = client.crypto.mnemonic_derive_sign_keys(phrase=phrase)
        public_safe = client.crypto.convert_public_key_to_ton_safe_format(
            public_key=keypair.public)
        self.assertEqual(
            'PuZhw8W5ejPJwKA68RL7sn4_RNmeH4BIU_mEK7em5d4_-cIx', public_safe)

        mnemonic = client.crypto.mnemonic_from_entropy(
            entropy='2199ebe996f14d9e4e2595113ad1e627')
        keypair = client.crypto.mnemonic_derive_sign_keys(phrase=mnemonic)
        public_safe = client.crypto.convert_public_key_to_ton_safe_format(
            public_key=keypair.public)
        self.assertEqual(
            'PuZdw_KyXIzo8IksTrERN3_WoAoYTyK7OvM-yaLk711sUIB3', public_safe)

    def test_nacl_sign_keypair_from_secret_key(self):
        keypair = client.crypto.nacl_sign_keypair_from_secret_key(
            secret='8fb4f2d256e57138fb310b0a6dac5bbc4bee09eb4821223a720e5b8e1f3dd674')
        self.assertEqual(
            'aa5533618573860a7e1bf19f34bd292871710ed5b2eafa0dcdbb33405f2231c6',
            keypair.public)

        with self.assertRaises(TonException):
            client.crypto.nacl_sign_keypair_from_secret_key(secret='0a')

    def test_nacl_sign(self):
        # Nacl sign data
        unsigned = base64.b64encode('Test Message'.encode())
        secret = '56b6a77093d6fdf14e593f36275d872d75de5b341942376b2a08759f3cbae78f1869b7ef29d58026217e9cf163cbfbd0de889bdf1bf4daebf5433a312f5b8d6e'
        signed = client.crypto.nacl_sign(unsigned=unsigned, secret=secret)
        self.assertEqual(
            '+wz+QO6l1slgZS5s65BNqKcu4vz24FCJz4NSAxef9lu0jFfs8x3PzSZRC+pn5k8+aJi3xYMA3BQzglQmjK3hA1Rlc3QgTWVzc2FnZQ==',
            signed)

        # Nacl sign open
        opened = client.crypto.nacl_sign_open(
            signed=signed, public='1869b7ef29d58026217e9cf163cbfbd0de889bdf1bf4daebf5433a312f5b8d6e')
        self.assertEqual(unsigned, opened.encode())

        # Nacl sign detached
        signature = client.crypto.nacl_sign_detached(
            unsigned=unsigned, secret=secret)
        self.assertEqual(
            'fb0cfe40eea5d6c960652e6ceb904da8a72ee2fcf6e05089cf835203179ff65bb48c57ecf31dcfcd26510bea67e64f3e6898b7c58300dc14338254268cade103',
            signature)

        with self.assertRaises(TonException):
            client.crypto.nacl_sign(unsigned='0==', secret=secret)

        with self.assertRaises(TonException):
            client.crypto.nacl_sign_open(signed=signed, public='0x00')

        with self.assertRaises(TonException):
            client.crypto.nacl_sign_detached(unsigned=100, secret=secret)

    def test_nacl_box_keypair(self):
        keypair = client.crypto.nacl_box_keypair()
        self.assertEqual(64, len(keypair.public))
        self.assertEqual(64, len(keypair.secret))
        self.assertNotEqual(keypair.public, keypair.secret)

    def test_nacl_box_keypair_from_secret_key(self):
        keypair = client.crypto.nacl_box_keypair_from_secret_key(
            secret='e207b5966fb2c5be1b71ed94ea813202706ab84253bdf4dc55232f82a1caf0d4')
        self.assertEqual(
            'a53b003d3ffc1e159355cb37332d67fc235a7feb6381e36c803274074dc3933a',
            keypair.public)

        with self.assertRaises(TonException):
            client.crypto.nacl_box_keypair_from_secret_key(secret='0x00')

    def test_nacl_box_and_open(self):
        decrypted = base64.b64encode('Test Message'.encode())
        nonce = 'cd7f99924bf422544046e83595dd5803f17536f5c9a11746'
        their_public = 'c4e2d9fe6a6baf8d1812b799856ef2a306291be7a7024837ad33a8530db79c6b'
        secret = 'd9b9dc5033fb416134e5d2107fdbacab5aadb297cb82dbdcd137d663bac59f7f'

        # Create nacl box
        box = client.crypto.nacl_box(
            decrypted=decrypted, nonce=nonce, their_public=their_public,
            secret=secret)
        self.assertEqual('li4XED4kx/pjQ2qdP0eR2d/K30uN94voNADxwA==', box)

        # Open nacl box
        opened = client.crypto.nacl_box_open(
            encrypted=box, nonce=nonce, their_public=their_public,
            secret=secret)
        self.assertEqual(decrypted, opened.encode())

        with self.assertRaises(TonException):
            client.crypto.nacl_box(
                decrypted='0x00', nonce=nonce, their_public='', secret=secret)

        with self.assertRaises(TonException):
            client.crypto.nacl_box_open(
                encrypted=box, nonce=nonce, their_public=their_public,
                secret='')

    def test_nacl_secret_box_and_open(self):
        decrypted = base64.b64encode('Test Message \' \" {} $=,?'.encode())
        nonce = '2a33564717595ebe53d91a785b9e068aba625c8453a76e45'
        key = '8f68445b4e78c000fe4d6b7fc826879c1e63e3118379219a754ae66327764bd8'

        # Create nacl secret box
        box = client.crypto.nacl_secret_box(
            decrypted=decrypted, nonce=nonce, key=key)
        self.assertEqual(
            'I6QZteixTdul0K0ldT+/U4QF0t/C1Q8RGyzQ2Hl7886DpW3/DK5ijg==', box)

        # Open nacl secret box
        opened = client.crypto.nacl_secret_box_open(
            encrypted=box, nonce=nonce, key=key)
        self.assertEqual(decrypted, opened.encode())

        with self.assertRaises(TonException):
            client.crypto.nacl_secret_box(
                decrypted='0x00', nonce=nonce, key=None)

        with self.assertRaises(TonException):
            client.crypto.nacl_secret_box_open(
                encrypted=box, nonce=nonce, key='')

    def test_scrypt(self):
        password = base64.b64encode('Test Password'.encode())
        salt = base64.b64encode('Test Salt'.encode())
        key = client.crypto.scrypt(
            password=password, salt=salt, log_n=10, r=8, p=16, dk_len=64)
        self.assertEqual(
            '52e7fcf91356eca55fc5d52f16f5d777e3521f54e3c570c9bbb7df58fc15add73994e5db42be368de7ebed93c9d4f21f9be7cc453358d734b04a057d0ed3626d',
            key)

        with self.assertRaises(TonException):
            client.crypto.scrypt(
                password=password, salt=salt, log_n=10, r=1, p=1, dk_len=0)
