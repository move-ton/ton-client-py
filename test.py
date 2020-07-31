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
own = TonWallet(ton=ton,mnemonic=mnemonic)
print(own.address())
print(own.deploy_wallet())