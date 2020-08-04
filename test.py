import logging
import ctypes
from lib import TonClient, TON_CLIENT_DEFAULT_SETUP, TonWallet
import time
import asyncio

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

ton = TonClient()
ton.setup()
print(ton.version())
mnemonic = "city awake search unlock milk thrive unfair biology enhance antenna exact enhance benefit disorder jelly enjoy churn delay struggle twice unique pepper rate execute"
own = TonWallet(ton=ton, mnemonic=mnemonic)
print(ton.random_generateBytes(5))
print(ton.fromMnemonic_ToKeyPair(ton.generateMnemonic(12)["result"]))
print(ton.ton_crc16(hex_text="432a"))

print(
    ton.mnemonic_from_entropy(
        hex_text="2199ebe996f14d9e4e2595113ad1e6276bd05e2e147e16c8ab8ad5d47d13b44fcf",
        wordCount=24))
print(ton.hdkey_xprv_public(
    'xprv9s21ZrQH143K2JF8RafpqtKiTbsbaxEeUaMnNHsm5o6wCW3z8ySyH4UxFVSfZ8n7ESu7fgir8imbZKLYVBxFPND1pniTZ81vKfd45EHKX73'))
print(
    ton.keystore_add(
        ton.fromMnemonic_ToKeyPair(
            ton.generateMnemonic()["result"])["result"]))
print(ton.keystore_remove(1))
print(ton.keystore_clear())


print(ton.sha256("test"))
print(ton.hdkey_xprv_public(
    'xprv9s21ZrQH143K2JF8RafpqtKiTbsbaxEeUaMnNHsm5o6wCW3z8ySyH4UxFVSfZ8n7ESu7fgir8imbZKLYVBxFPND1pniTZ81vKfd45EHKX73'))


print(
    ton.hdkey_xprv_from_mnemonic(mnemonic))
print(ton.mnemonic_verify(mnemonic))

print(ton.ton_public_key_string(
    "72aad44ae5c7484d5cb5b652de00f01d46bb551966bebb61fa217da16425a0c9"))
print(ton.nacl_box_keypair())
print(ton.ed25519_keypair())
print(ton.hdkey_xprv_derive(
    'xprv9s21ZrQH143K2JF8RafpqtKiTbsbaxEeUaMnNHsm5o6wCW3z8ySyH4UxFVSfZ8n7ESu7fgir8imbZKLYVBxFPND1pniTZ81vKfd45EHKX73', 1))
print(ton.modularPower('1', '1', '1'))
print(ton.factorize('a5'))
print(ton.nacl_sign_keypair())
print(ton.nacl_sign_keypair_from_secret_key(
    "401053c890ffbf4b0651d410814864ba3924360cd5455e7f078bc71f698bd32d7f49ce39a35ec7878d4325754a21977392c7fccd3a206693c4f263f39a9e6a29"))

# print(own.address())
# print(own.deploy_wallet())
print(
    ton.nacl_box(
        message="lol",
        nonce="2",
        their_public_key="2c04f5ef0b62a91a140fd3871d9e6f3f722a9e38f56ced35184d9ed2679379e7"))
print(ton.nacl_box_keypair_from_secret_key(
    "401053c890ffbf4b0651d410814864ba3924360cd5455e7f078bc71f698bd32d7f49ce39a35ec7878d4325754a21977392c7fccd3a206693c4f263f39a9e6a29"))
print(
    ton.scrypt(
        "lol",
        salt="lasdokaskdasd",
        password="lol",
        logn=2,
        r=4324234,
        p=3847534, dk_len=42))
print(ton.nacl_sign("X08", message="1234"))
print(
    ton.nacl_secret_box_open(
        'X08',
        "72aad44ae5c7484d5cb5b652de00f01d46bb551966bebb61fa217da16425a0c9",
        "lol"))
print(ton.nacl_sign_detached('X08', message="lol"))
print(ton.nacl_secret_box("X08", "X08", message="lol"))
print(ton.nacl_box_open("X08", "X08", "X08", message="lol"))
print(ton.nacl_sign_open("X08", message="lol"))
