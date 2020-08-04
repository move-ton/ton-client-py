import unittest
import base64
import logging

from tonsdk.lib import TonClient

logging.basicConfig(level=logging.INFO)


class TestCrypto(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TonClient()
        self.mnemonic = "machine logic master small before pole ramp ankle stage trash pepper success oxygen unhappy engine muscle party oblige situate cement fame keep inform lemon"
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
        self.assertEqual(keys, {"public": "2e750ea795aad6e04ae1544132619c6a5e1356c36db60532320dae6aa656cf2e", "secret": "7ee962326304f9f88d5048fabdde7921411b1aad6400ef984c85a0a9cb3b1a7c"})

    def test_ton_crc16(self):
        # CRC from plain text
        crc = self.client.ton_crc16(
            string=self.text_plain, fmt=TonClient.TYPE_TEXT)
        self.assertEqual(crc, self.text_valid_crc16)

        # CRC from hex
        crc = self.client.ton_crc16(
            string=self.text_hex, fmt=TonClient.TYPE_HEX)
        self.assertEqual(crc, self.text_valid_crc16)

        # CRC from base64
        crc = self.client.ton_crc16(
            string=self.text_base64, fmt=TonClient.TYPE_BASE64)
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
            entropy=hex_entropy, fmt=TonClient.TYPE_HEX, word_count=24)
        self.assertEqual(mnemonic_from_hex, mnemonic)

        # Mnemonic from base64 entropy
        mnemonic_from_b64 = self.client.mnemonic_from_entropy(
            entropy=b64_entropy, fmt=TonClient.TYPE_BASE64, word_count=24)
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
            string=self.text_plain, fmt=TonClient.TYPE_TEXT)
        self.assertEqual(sha, self.text_valid_sha512)

        # SHA512 from hex string
        sha = self.client.sha512(string=self.text_hex, fmt=TonClient.TYPE_HEX)
        self.assertEqual(sha, self.text_valid_sha512)

        # SHA512 from base64
        sha = self.client.sha512(
            string=self.text_base64, fmt=TonClient.TYPE_BASE64)
        self.assertEqual(sha, self.text_valid_sha512)

    def test_sha256(self):
        # SHA256 from plain text
        sha = self.client.sha256(
            string=self.text_plain, fmt=TonClient.TYPE_TEXT)
        self.assertEqual(sha, self.text_valid_sha256)

        # SHA256 from hex string
        sha = self.client.sha256(string=self.text_hex, fmt=TonClient.TYPE_HEX)
        self.assertEqual(sha, self.text_valid_sha256)

        # SHA256 from base64
        sha = self.client.sha256(
            string=self.text_base64, fmt=TonClient.TYPE_BASE64)
        self.assertEqual(sha, self.text_valid_sha256)
