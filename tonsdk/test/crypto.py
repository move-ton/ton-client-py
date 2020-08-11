import unittest
import base64
import logging

from tonsdk.lib import TonClient, DEVNET_BASE_URL

logging.basicConfig(level=logging.INFO)


class TestCrypto(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TonClient(servers=[DEVNET_BASE_URL])

        self.mnemonic = "machine logic master small before pole ramp ankle stage trash pepper success oxygen unhappy engine muscle party oblige situate cement fame keep inform lemon"
        self.keypair = {
            "public": "2e750ea795aad6e04ae1544132619c6a5e1356c36db60532320dae6aa656cf2e",
            "secret": "7ee962326304f9f88d5048fabdde7921411b1aad6400ef984c85a0a9cb3b1a7c"
        }
        self.public_b64 = "PuYudQ6nlarW4ErhVEEyYZxqXhNWw222BTIyDa5qplbPLjlF"
        self.bip32_key = "xprv9s21ZrQH143K41qESFSVMwMgA2qvjYdjJo4wz9QWgH2G5yiFG5Ep8rVZsm2zn87CwBR7GYjJY57GLs529NhXsRvpm9M9vJ62WD7tA5J6gPs"
        self.bip32_secret = "8a5f38321a53581415f11fb7e056ef703136b4e58d491bd702985db42dec25f4"
        self.bip32_public = "03b03351fc4928f337c11ef01ade9109e5fd47f348c01e7bc64020208e819201bb"
        self.derivation_path = "m/44'/60'/0'/0"
        self.derived = "xprvA1N8muEo6dX1RVmzgDPULAmkKaKqrXio2cpyxUSYcEttvfF65p5vFnkzgirWNq8EyD4DWFu9diZ1gGJnxHNe7exU4fNTKWurZfDt2kykTNK"
        self.derived_0 = "xprv9uY18qvpBDuj1ejUbdpgYN8ENMWz3sze73RhNqq1tZvzayH54KFC9GAUReKmJUTNJHF9gsHwjGs3wvyWAHFAHZ6VshF9KZp96S8th5A4ti2"
        self.keypair_nacl_sign = {  # Keypair from self.keypair["secret"]
            "public": "b4d426cf444a9aef30c913527208c58726af96876f16a7dc38b7b27cfedb3352",
            "secret": "7ee962326304f9f88d5048fabdde7921411b1aad6400ef984c85a0a9cb3b1a7c"
        }

        self.text_plain = "Test"
        self.text_hex = self.text_plain.encode().hex()
        self.text_base64 = base64.b64encode(self.text_plain.encode()).decode()
        self.text_valid_crc16 = 44104
        self.text_valid_sha512 = "c6ee9e33cf5c6715a1d148fd73f7318884b41adcb916021e2bc0e800a5c5dd97f5142178f6ae88c8fdd98e1afb0ce4c8d2c54b5f37b30b7da1997bb33b0b8a31"
        self.text_valid_sha256 = "532eaabd9574880dbf76b9b8cc00832c20a6ec113d682299550d7a6e0f345e25"

    def test_random_generate_bytes(self):
        bts = self.client.random_generate_bytes(length=8)
        self.assertEqual(len(bts), 16)

    def test_derive_sign_keys(self):
        keys = self.client.derive_sign_keys(mnemonic=self.mnemonic)
        self.assertEqual(keys, self.keypair)

    def test_ton_crc16(self):
        # CRC from plain text
        crc = self.client.ton_crc16(
            string=self.text_plain, string_fmt=TonClient.TYPE_TEXT)
        self.assertEqual(crc, self.text_valid_crc16)

        # CRC from hex
        crc = self.client.ton_crc16(
            string=self.text_hex, string_fmt=TonClient.TYPE_HEX)
        self.assertEqual(crc, self.text_valid_crc16)

        # CRC from base64
        crc = self.client.ton_crc16(
            string=self.text_base64, string_fmt=TonClient.TYPE_BASE64)
        self.assertEqual(crc, self.text_valid_crc16)

    def test_mnemonic_generate(self):
        mnemonic = self.client.mnemonic_generate(word_count=12)
        self.assertEqual(len(mnemonic.split(" ")), 12)

        mnemonic = self.client.mnemonic_generate()
        self.assertEqual(len(mnemonic.split(" ")), 24)

    def test_mnemonic_from_entropy(self):
        hex_entropy = "2199ebe996f14d9e4e2595113ad1e6276bd05e2e147e16c8ab8ad5d47d13b44fcf"
        b64_entropy = base64.b64encode(bytes.fromhex(hex_entropy)).decode()
        mnemonic = "category purpose insane bonus orbit pole clerk news drama eager vibrant raven patch nut pause lawn actress quality shed essence wing age laundry soon"

        # Mnemonic from hex entropy
        mnemonic_from_hex = self.client.mnemonic_from_entropy(
            entropy=hex_entropy, entropy_fmt=TonClient.TYPE_HEX, word_count=24)
        self.assertEqual(mnemonic_from_hex, mnemonic)

        # Mnemonic from base64 entropy
        mnemonic_from_b64 = self.client.mnemonic_from_entropy(
            entropy=b64_entropy, entropy_fmt=TonClient.TYPE_BASE64,
            word_count=24)
        self.assertEqual(mnemonic_from_b64, mnemonic)

        self.assertEqual(mnemonic_from_hex, mnemonic_from_b64)

    def test_mnemonic_verify(self):
        is_valid = self.client.mnemonic_verify(mnemonic=self.mnemonic)
        self.assertEqual(is_valid, True)

        is_valid = self.client.mnemonic_verify(mnemonic="word word word")
        self.assertEqual(is_valid, False)

    def test_mnemonic_words(self):
        wordlist = self.client.mnemonic_words()
        self.assertEqual(len(wordlist.split(" ")), 2048)

    def test_sha512(self):
        # SHA512 from plain text
        sha = self.client.sha512(
            string=self.text_plain, string_fmt=TonClient.TYPE_TEXT)
        self.assertEqual(sha, self.text_valid_sha512)

        # SHA512 from hex string
        sha = self.client.sha512(
            string=self.text_hex, string_fmt=TonClient.TYPE_HEX)
        self.assertEqual(sha, self.text_valid_sha512)

        # SHA512 from base64
        sha = self.client.sha512(
            string=self.text_base64, string_fmt=TonClient.TYPE_BASE64)
        self.assertEqual(sha, self.text_valid_sha512)

    def test_sha256(self):
        # SHA256 from plain text
        sha = self.client.sha256(
            string=self.text_plain, string_fmt=TonClient.TYPE_TEXT)
        self.assertEqual(sha, self.text_valid_sha256)

        # SHA256 from hex string
        sha = self.client.sha256(
            string=self.text_hex, string_fmt=TonClient.TYPE_HEX)
        self.assertEqual(sha, self.text_valid_sha256)

        # SHA256 from base64
        sha = self.client.sha256(
            string=self.text_base64, string_fmt=TonClient.TYPE_BASE64)
        self.assertEqual(sha, self.text_valid_sha256)

    def test_scrypt(self):
        result = self.client.scrypt(
            data="Test", n=2, r=4, p=1, dk_len=32, salt="salt",
            salt_fmt=TonClient.TYPE_TEXT, password="password",
            password_fmt=TonClient.TYPE_TEXT)
        self.assertEqual(result, "01f4a6ab0123db7d5f4a3c50612774479af9b63548b161d093b40c1e87c953cc")

    def test_keystore_add(self):
        result = self.client.keystore_add(keypair=self.keypair)
        self.assertEqual(result.isnumeric(), True)

    def test_hdkey_xprv_from_mnemonic(self):
        key = self.client.hdkey_xprv_from_mnemonic(mnemonic=self.mnemonic)
        self.assertEqual(key, self.bip32_key)

    def test_hdkey_xprv_secret(self):
        secret = self.client.hdkey_xprv_secret(bip32_key=self.bip32_key)
        self.assertEqual(secret, self.bip32_secret)

    def test_hdkey_xprv_public(self):
        public = self.client.hdkey_xprv_public(bip32_key=self.bip32_key)
        self.assertEqual(public, self.bip32_public)

    def test_hdkey_xprv_derive_path(self):
        result = self.client.hdkey_xprv_derive_path(
            bip32_key=self.bip32_key, derive_path=self.derivation_path)
        self.assertEqual(result, self.derived)

    def test_hdkey_xprv_derive(self):
        index = 0
        result = self.client.hdkey_xprv_derive(
            bip32_key=self.bip32_key, index=index)
        self.assertEqual(result, getattr(self, f"derived_{index}"))

    def test_factorize(self):
        result = self.client.factorize(number="2a")
        self.assertEqual(result, {'a': '3', 'b': 'E'})

    def test_ton_public_key_string(self):
        public = self.client.ton_public_key_string(
            public_key=self.keypair["public"])
        self.assertEqual(public, self.public_b64)

    def test_ed25519_keypair(self):
        keypair = self.client.ed25519_keypair()
        self.assertEqual(type(keypair), dict)
        self.assertEqual(list(keypair.keys()), ["public", "secret"])

    def test_modular_power(self):
        result = self.client.modular_power(base="1", exponent="2", modulus="5")
        self.assertEqual(result.isnumeric(), True)

    def test_nacl_box_keypair(self):
        keypair = self.client.nacl_box_keypair()
        self.assertEqual(type(keypair), dict)
        self.assertEqual(list(keypair.keys()), ["public", "secret"])

    def test_nacl_sign_keypair(self):
        keypair = self.client.nacl_sign_keypair()
        self.assertEqual(type(keypair), dict)
        self.assertEqual(list(keypair.keys()), ["public", "secret"])

    def test_nacl_sign_keypair_from_secret_key(self):
        keypair = self.client.nacl_box_keypair_from_secret_key(
            key=self.keypair["secret"])
        self.assertEqual(keypair, self.keypair_nacl_sign)

    def test_nacl_box(self):
        # TODO: Got an error 'Either Key or Keystore Handle must be specified'
        pass

    def test_nacl_sign(self):
        signed = self.client.nacl_sign(
            key="".join(self.keypair_nacl_sign.values()), message="Test",
            message_fmt=TonClient.TYPE_TEXT)
        self.assertEqual(signed, "a070fb8ecbcfcc283b999290a099d7821b3c2f8a86ec1ac1e6b0da4d5a005f997dda5a2d8cc17a97ba80906ee6cc29690403ecbeacdf730112abaf1f3f07440354657374")

    def test_nacl_secret_box_open(self):
        # TODO: Got an error 'Invalid key size 1. Expected 24.'
        pass

    def test_nacl_sign_detached(self):
        signed = self.client.nacl_sign_detached(
            key="".join(self.keypair_nacl_sign.values()), message="Test",
            message_fmt=TonClient.TYPE_TEXT)
        self.assertEqual(signed, "a070fb8ecbcfcc283b999290a099d7821b3c2f8a86ec1ac1e6b0da4d5a005f997dda5a2d8cc17a97ba80906ee6cc29690403ecbeacdf730112abaf1f3f074403")

    def test_nacl_secret_box(self):
        # TODO: Got an error 'Invalid key size 1. Expected 24.'
        pass

    def test_nacl_box_open(self):
        # TODO: Got an error 'Invalid key size 1. Expected 24.'
        pass

    def test_nacl_sign_open(self):
        # TODO: ...
        pass
