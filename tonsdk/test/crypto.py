import unittest
import base64
import logging

from tonsdk.lib import TonClient

logging.basicConfig(level=logging.DEBUG)


class TestCrypto(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TonClient()
        self.mnemonic = "machine logic master small before pole ramp ankle stage trash pepper success oxygen unhappy engine muscle party oblige situate cement fame keep inform lemon"

    def test_random_generate_bytes(self):
        bts = self.client.random_generate_bytes(8)
        self.assertEqual(len(bts), 16)

    def test_derive_sign_keys(self):
        keys = self.client.derive_sign_keys(self.mnemonic)
        self.assertEqual(keys, {"public": "2e750ea795aad6e04ae1544132619c6a5e1356c36db60532320dae6aa656cf2e", "secret": "7ee962326304f9f88d5048fabdde7921411b1aad6400ef984c85a0a9cb3b1a7c"})

    def test_ton_crc16(self):
        # CRC from plain text
        crc = self.client.ton_crc16("Test")
        self.assertEqual(crc, 26235)

        # CRC from hex
        crc = self.client.ton_crc16("0x1111")
        self.assertEqual(crc, 12882)

        # CRC from base64
        crc = self.client.ton_crc16("UQAasiw2QhTiS3grxJZuI4dLHAzGgujbotJKBWG7J9BCIczW")
        self.assertEqual(crc, 0)

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
            entropy=hex_entropy, word_count=24)
        self.assertEqual(mnemonic_from_hex, mnemonic)

        # Mnemonic from base64 entropy
        mnemonic_from_b64 = self.client.mnemonic_from_entropy(
            entropy=b64_entropy, word_count=24)
        self.assertEqual(mnemonic_from_b64, mnemonic)

        self.assertEqual(mnemonic_from_hex, mnemonic_from_b64)

    def test_mnemonic_verify(self):
        is_valid = self.client.mnemonic_verify(self.mnemonic)
        self.assertEqual(is_valid, True)

        is_valid = self.client.mnemonic_verify("word word word")
        self.assertEqual(is_valid, False)

    def test_mnemonic_words(self):
        wordlist = self.client.mnemonic_words()
        self.assertEqual(len(wordlist.split(" ")), 2048)

    def test_sha512(self):
        # SHA512 from plain text
        sha = self.client.sha512("Test")
        self.assertEqual(sha, "8c0cc317ddad4a3fad5d51789784f910dfa463c358462ab3e10ca0bba2b5478827cd90f4d058df0f1ed6fe98ffca7253946aeef6a3a7f1dd03745d7ab28690ee")

        # SHA512 from hex string
        sha = self.client.sha512("0x1111")
        self.assertEqual(sha, "7663cbe5bd6631a41ccbb8d3af07fa8247b91c90823999091f66ca40a10ca584a6cd52614cab51b8e9750bcf96639d4cf95c4006d970711a0bbe7c0c878d772d")

        # SHA512 from base64
        sha = self.client.sha512("UQAasiw2QhTiS3grxJZuI4dLHAzGgujbotJKBWG7J9BCIczW")
        self.assertEqual(sha, "8740ee6485930f142f051b03ffe72596695a4f04f64be55e0cd525a107bf2ede679711ac8802027c31675601068c895179ab4d0273a9f8da2981793d01021623")

    def test_sha256(self):
        str_plain = "Test"
        str_hex = str_plain.encode().hex()
        str_b64 = base64.b64encode(str_plain.encode()).decode()

        print(str_plain, str_hex, str_b64)

        # SHA256 from plain text
        sha = self.client.sha256(str_plain)
        # self.assertEqual(sha, "1553b4e031d629c794ede30740378d5e7c723bede1b596d6fe0935f80b169f05")

        # SHA256 from hex string
        # sha = self.client.sha256(str_hex)
        # print(sha)
        # self.assertEqual(sha, "140ad0841b7999e39160d942527b215b312137061143e29095a2f7638bb8711a")

        # SHA256 from base64
        # sha = self.client.sha256(str_b64)
        # print(sha)
        # self.assertEqual(sha, "8740ee6485930f142f051b03ffe72596695a4f04f64be55e0cd525a107bf2ede679711ac8802027c31675601068c895179ab4d0273a9f8da2981793d01021623")
