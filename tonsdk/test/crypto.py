import json
import unittest
import base64
import logging
from io import StringIO

from tonsdk.client import TonClient, DEVNET_BASE_URL
from tonsdk.crypto.types import KeyPair, FmtString, NaclBox
from tonsdk.errors import TonException

logging.basicConfig(level=logging.INFO)
client = TonClient(servers=[DEVNET_BASE_URL])


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


class TestCrypto(unittest.TestCase):
    def setUp(self) -> None:
        self.mnemonic = "machine logic master small before pole ramp ankle stage trash pepper success oxygen unhappy engine muscle party oblige situate cement fame keep inform lemon"
        self.mnemonic_keypair = KeyPair(**{
            "public": "2e750ea795aad6e04ae1544132619c6a5e1356c36db60532320dae6aa656cf2e",
            "secret": "7ee962326304f9f88d5048fabdde7921411b1aad6400ef984c85a0a9cb3b1a7c"
        })
        self.keypair_public_b64 = "PuYudQ6nlarW4ErhVEEyYZxqXhNWw222BTIyDa5qplbPLjlF"

        self.mnemonic_bip32_key = "xprv9s21ZrQH143K41qESFSVMwMgA2qvjYdjJo4wz9QWgH2G5yiFG5Ep8rVZsm2zn87CwBR7GYjJY57GLs529NhXsRvpm9M9vJ62WD7tA5J6gPs"
        self.bip32_key_secret = "8a5f38321a53581415f11fb7e056ef703136b4e58d491bd702985db42dec25f4"
        self.bip32_key_public = "03b03351fc4928f337c11ef01ade9109e5fd47f348c01e7bc64020208e819201bb"
        self.derivation_path = "m/44'/60'/0'/0"
        self.derived = "xprvA1N8muEo6dX1RVmzgDPULAmkKaKqrXio2cpyxUSYcEttvfF65p5vFnkzgirWNq8EyD4DWFu9diZ1gGJnxHNe7exU4fNTKWurZfDt2kykTNK"
        self.derived_0 = "xprv9uY18qvpBDuj1ejUbdpgYN8ENMWz3sze73RhNqq1tZvzayH54KFC9GAUReKmJUTNJHF9gsHwjGs3wvyWAHFAHZ6VshF9KZp96S8th5A4ti2"

        self.keypair_nacl = KeyPair(**{
            "public": "b4d426cf444a9aef30c913527208c58726af96876f16a7dc38b7b27cfedb3352",
            "secret": "7ee962326304f9f88d5048fabdde7921411b1aad6400ef984c85a0a9cb3b1a7c"
        })  # From 'mnemonic_keypair.secret'
        self.keypair_nacl_random = KeyPair(**{
            "public": "5c46510978b0c0f3f3b5f7491468d02572ff08794fdebb304fb8d8423d429603",
            "secret": "eee6caf1c4c34b4a2d3fe16a99ff5ffbfdef00afa74b3fb7faae324d9836e74b"
        })  # Random keypair
        self.keypair_nacl_sign = KeyPair(**{
            "public": "2e750ea795aad6e04ae1544132619c6a5e1356c36db60532320dae6aa656cf2e",
            "secret": "7ee962326304f9f88d5048fabdde7921411b1aad6400ef984c85a0a9cb3b1a7c2e750ea795aad6e04ae1544132619c6a5e1356c36db60532320dae6aa656cf2e"
        })  # From 'mnemonic_keypair.secret'
        self.nacl_box = NaclBox(
            key=self.keypair_nacl.secret, message="Test").as_text()

        self.text_plain = "Test"
        self.text_hex = self.text_plain.encode().hex()
        self.text_base64 = base64.b64encode(self.text_plain.encode()).decode()
        self.text_valid_crc16 = 44104
        self.text_valid_sha512 = "c6ee9e33cf5c6715a1d148fd73f7318884b41adcb916021e2bc0e800a5c5dd97f5142178f6ae88c8fdd98e1afb0ce4c8d2c54b5f37b30b7da1997bb33b0b8a31"
        self.text_valid_sha256 = "532eaabd9574880dbf76b9b8cc00832c20a6ec113d682299550d7a6e0f345e25"

    def test_random_generate_bytes(self):
        bts = client.crypto.random_generate_bytes(length=8)
        self.assertEqual(len(bts), 16)

        def __callable():
            client.crypto.random_generate_bytes(length=-1)
        self.assertRaises(TonException, __callable)

    def test_mnemonic_derive_sign_keys(self):
        key_pair = client.crypto.mnemonic_derive_sign_keys(
            mnemonic=self.mnemonic)
        self.assertIsInstance(key_pair, KeyPair)
        self.assertEqual(key_pair.dict, self.mnemonic_keypair.dict)

        def __callable():
            client.crypto.mnemonic_derive_sign_keys(mnemonic="wrong")
        self.assertRaises(TonException, __callable)

    def test_mnemonic_from_random(self):
        mnemonic = client.crypto.mnemonic_from_random(word_count=12)
        self.assertEqual(len(mnemonic.split(" ")), 12)

        mnemonic = client.crypto.mnemonic_from_random()
        self.assertEqual(len(mnemonic.split(" ")), 24)

        def __callable():
            client.crypto.mnemonic_from_random(word_count=0)
        self.assertRaises(TonException, __callable)

    def test_mnemonic_from_entropy(self):
        hex_entropy = "2199ebe996f14d9e4e2595113ad1e6276bd05e2e147e16c8ab8ad5d47d13b44fcf"
        b64_entropy = base64.b64encode(bytes.fromhex(hex_entropy)).decode()
        mnemonic = "category purpose insane bonus orbit pole clerk news drama eager vibrant raven patch nut pause lawn actress quality shed essence wing age laundry soon"

        # Mnemonic from hex entropy
        m_hex = client.crypto.mnemonic_from_entropy(
            entropy_fmt=FmtString(hex_entropy).hex, word_count=24)
        self.assertEqual(m_hex, mnemonic)

        # Mnemonic from base64 entropy
        m_b64 = client.crypto.mnemonic_from_entropy(
            entropy_fmt=FmtString(b64_entropy).base64, word_count=24)
        self.assertEqual(m_b64, mnemonic)

        self.assertEqual(m_hex, m_b64)

    def test_mnemonic_verify(self):
        is_valid = client.crypto.mnemonic_verify(mnemonic=self.mnemonic)
        self.assertEqual(is_valid, True)

        is_valid = client.crypto.mnemonic_verify(mnemonic="word word word")
        self.assertEqual(is_valid, False)

    def test_mnemonic_words(self):
        wordlist = client.crypto.mnemonic_words()
        self.assertEqual(len(wordlist.split(" ")), 2048)

    def test_ton_crc16(self):
        # CRC from plain text
        crc = client.crypto.ton_crc16(
            string_fmt=FmtString(self.text_plain).text)
        self.assertEqual(crc, self.text_valid_crc16)

        # CRC from hex
        crc = client.crypto.ton_crc16(
            string_fmt=FmtString(self.text_hex).hex)
        self.assertEqual(crc, self.text_valid_crc16)

        # CRC from base64
        crc = client.crypto.ton_crc16(
            string_fmt=FmtString(self.text_base64).base64)
        self.assertEqual(crc, self.text_valid_crc16)

        # Wrong format
        def __callable():
            client.crypto.ton_crc16(string_fmt=FmtString("T").hex)

        self.assertRaises(TonException, __callable)

    def test_sha512(self):
        # SHA512 from plain text
        sha = client.crypto.sha512(string_fmt=FmtString(self.text_plain).text)
        self.assertEqual(sha, self.text_valid_sha512)

        # SHA512 from hex string
        sha = client.crypto.sha512(string_fmt=FmtString(self.text_hex).hex)
        self.assertEqual(sha, self.text_valid_sha512)

        # SHA512 from base64
        sha = client.crypto.sha512(
            string_fmt=FmtString(self.text_base64).base64)
        self.assertEqual(sha, self.text_valid_sha512)

        # Wrong format
        def __callable():
            client.crypto.sha512(string_fmt=FmtString("T").hex)

        self.assertRaises(TonException, __callable)

    def test_sha256(self):
        # SHA256 from plain text
        sha = client.crypto.sha256(string_fmt=FmtString(self.text_plain).text)
        self.assertEqual(sha, self.text_valid_sha256)

        # SHA256 from hex string
        sha = client.crypto.sha256(string_fmt=FmtString(self.text_hex).hex)
        self.assertEqual(sha, self.text_valid_sha256)

        # SHA256 from base64
        sha = client.crypto.sha256(
            string_fmt=FmtString(self.text_base64).base64)
        self.assertEqual(sha, self.text_valid_sha256)

        # Wrong format
        def __callable():
            client.crypto.sha256(string_fmt=FmtString("T").hex)

        self.assertRaises(TonException, __callable)

    def test_scrypt(self):
        result = client.crypto.scrypt(
            data="Test", n=2, r=4, p=1, dk_len=32,
            salt_fmt=FmtString("salt").text,
            password_fmt=FmtString("password").text)
        self.assertEqual(result, "01f4a6ab0123db7d5f4a3c50612774479af9b63548b161d093b40c1e87c953cc")

    def test_hdkey_xprv_from_mnemonic(self):
        key = client.crypto.hdkey_xprv_from_mnemonic(mnemonic=self.mnemonic)
        self.assertEqual(key, self.mnemonic_bip32_key)

    def test_hdkey_xprv_secret(self):
        secret = client.crypto.hdkey_xprv_secret(
            bip32_key=self.mnemonic_bip32_key)
        self.assertEqual(secret, self.bip32_key_secret)

        def __callable():
            client.crypto.hdkey_xprv_secret(bip32_key="0x00")

        self.assertRaises(TonException, __callable)

    def test_hdkey_xprv_public(self):
        public = client.crypto.hdkey_xprv_public(
            bip32_key=self.mnemonic_bip32_key)
        self.assertEqual(public, self.bip32_key_public)

        def __callable():
            client.crypto.hdkey_xprv_public(bip32_key="0x00")

        self.assertRaises(TonException, __callable)

    def test_hdkey_xprv_derive_path(self):
        result = client.crypto.hdkey_xprv_derive_path(
            bip32_key=self.mnemonic_bip32_key,
            derive_path=self.derivation_path)
        self.assertEqual(result, self.derived)

        def __callable():
            client.crypto.hdkey_xprv_derive_path(
                bip32_key=self.mnemonic_bip32_key, derive_path="m//60'/0'/0")

        self.assertRaises(TonException, __callable)

    def test_hdkey_xprv_derive(self):
        result = client.crypto.hdkey_xprv_derive(
            bip32_key=self.mnemonic_bip32_key, index=0)
        self.assertEqual(result, getattr(self, f"derived_{0}"))

        def __callable():
            client.crypto.hdkey_xprv_derive(
                bip32_key=self.mnemonic_bip32_key, index=-1)

        self.assertRaises(TonException, __callable)

    def test_factorize(self):
        result = client.crypto.factorize(number="2a")
        self.assertEqual(list(result.keys()), ["a", "b"])

    def test_ton_public_key_string(self):
        public = client.crypto.ton_public_key_string(
            public_key=self.mnemonic_keypair.public)
        self.assertEqual(public, self.keypair_public_b64)

    def test_ed25519_keypair(self):
        keypair = client.crypto.ed25519_keypair()
        self.assertIsInstance(keypair, KeyPair)
        self.assertIsNotNone(keypair.secret)
        self.assertIsNotNone(keypair.public)

    def test_math_modular_power(self):
        result = client.crypto.math_modular_power(
            base=1, exponent=2, modulus=5)
        self.assertEqual(result.isnumeric(), True)

        def __callable_base():
            client.crypto.math_modular_power(base=1.1, exponent=2, modulus=5)
        self.assertRaises(TonException, __callable_base)

        def __callable_exponent():
            client.crypto.math_modular_power(base=1, exponent=2.1, modulus=5)
        self.assertRaises(TonException, __callable_exponent)

        def __callable_modulus_float():
            client.crypto.math_modular_power(base=1, exponent=2, modulus=5.1)
        self.assertRaises(TonException, __callable_modulus_float)

        def __callable_modulus_zero():
            client.crypto.math_modular_power(base=1, exponent=2, modulus=0)
        self.assertRaises(ValueError, __callable_modulus_zero)

    def test_nacl_box_keypair(self):
        keypair = client.crypto.nacl_box_keypair()
        self.assertIsInstance(keypair, KeyPair)
        self.assertIsNotNone(keypair.public)
        self.assertIsNotNone(keypair.secret)

    def test_nacl_box_keypair_from_secret_key(self):
        keypair = client.crypto.nacl_box_keypair_from_secret_key(
            secret_key=self.mnemonic_keypair.secret)
        self.assertIsInstance(keypair, KeyPair)
        self.assertEqual(keypair.secret, self.keypair_nacl.secret)
        self.assertEqual(keypair.public, self.keypair_nacl.public)

    def test_nacl_sign_keypair(self):
        keypair = client.crypto.nacl_sign_keypair()
        self.assertEqual(type(keypair), KeyPair)
        self.assertIsNotNone(keypair.public)
        self.assertIsNotNone(keypair.secret)

    def test_nacl_sign_keypair_from_secret_key(self):
        keypair = client.crypto.nacl_sign_keypair_from_secret_key(
            secret_key=self.mnemonic_keypair.secret)
        self.assertEqual(keypair.public, self.keypair_nacl_sign.public)
        self.assertEqual(keypair.secret, self.keypair_nacl_sign.secret)

    def test_nacl_box(self):
        box = client.crypto.nacl_box(
            nonce="cd7f99924bf422544046e83595dd5803f17536f5c9a11746",
            their_public=self.keypair_nacl_random.public, box=self.nacl_box)
        self.assertEqual(box, "091b6f2905d706e9506a4ed3597b7cf6fdd63ca1")

    def test_nacl_box_open(self):
        # Nonce from 'test_nacl_box'
        nonce = "cd7f99924bf422544046e83595dd5803f17536f5c9a11746"
        # Message from 'test_nacl_box'
        message = "091b6f2905d706e9506a4ed3597b7cf6fdd63ca1"
        nacl_box = NaclBox(
            key=self.keypair_nacl_random.secret, message=message,
            output=NaclBox.OUTPUT_TEXT).as_hex()

        opened = client.crypto.nacl_box_open(
            nonce=nonce, their_public=self.keypair_nacl.public, box=nacl_box)
        self.assertEqual(opened, "Test")

    def test_nacl_sign(self):
        self.nacl_box.key = self.keypair_nacl_sign.secret
        self.nacl_box.output = NaclBox.OUTPUT_BASE64
        signed = client.crypto.nacl_sign(box=self.nacl_box)
        self.assertEqual(signed, "VI2KBqLgEHWqcvAXJi4WdWKzkF3p3eXBnAyy2rgpBgTb3HYsOPOpt028mkXzPMoqxC6fLA/Chfk0JWkbtDl5AlRlc3Q=")

    def test_nacl_sign_open(self):
        # Message from 'test_nacl_sign'
        message = "VI2KBqLgEHWqcvAXJi4WdWKzkF3p3eXBnAyy2rgpBgTb3HYsOPOpt028mkXzPMoqxC6fLA/Chfk0JWkbtDl5AlRlc3Q="
        box = NaclBox(
            key=self.keypair_nacl_sign.public, message=message,
            output=NaclBox.OUTPUT_TEXT).as_base64()

        opened = client.crypto.nacl_sign_open(box=box)
        self.assertEqual(opened, "Test")

    def test_nacl_sign_detached(self):
        self.nacl_box.key = self.keypair_nacl_sign.secret
        self.nacl_box.output = NaclBox.OUTPUT_HEX_UP
        signed = client.crypto.nacl_sign_detached(self.nacl_box)
        self.assertEqual(signed, "548D8A06A2E01075AA72F017262E167562B3905DE9DDE5C19C0CB2DAB8290604DBDC762C38F3A9B74DBC9A45F33CCA2AC42E9F2C0FC285F93425691BB4397902")

    def test_nacl_secret_box(self):
        box = client.crypto.nacl_secret_box(
            nonce="cd7f99924bf422544046e83595dd5803f17536f5c9a11746",
            box=self.nacl_box)
        self.assertEqual(box, "2291ee3ab6f40091aa9ede55a345572ca0418dc6")

    def test_nacl_secret_box_open(self):
        # Nonce from 'test_nacl_secret_box'
        nonce = "cd7f99924bf422544046e83595dd5803f17536f5c9a11746"
        # Box from 'test_nacl_secret_box'
        message = "2291ee3ab6f40091aa9ede55a345572ca0418dc6"

        box = NaclBox(
            key=self.keypair_nacl.secret, message=message,
            output=NaclBox.OUTPUT_TEXT).as_hex()
        opened = client.crypto.nacl_secret_box_open(nonce=nonce, box=box)
        self.assertEqual(opened, "Test")
