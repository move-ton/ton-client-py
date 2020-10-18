import os

from tonclient.client import TonClient, DEVNET_BASE_URL
from tonclient.types import Abi, KeyPair, MessageSource, Signer, CallSet

BASE_DIR = os.path.dirname(__file__)
SAMPLES_DIR = os.path.join(BASE_DIR, 'samples')
WALLET_ADDRESS = '0:7ecb2f57fb27f26423eb524f8c2fcbae8182a2b7cef9f2dfe5d76e51327ffe64'

async_core_client = TonClient(network={'server_address': DEVNET_BASE_URL})
sync_core_client = TonClient(
    network={'server_address': DEVNET_BASE_URL}, is_core_async=False)


def send_grams(address: str, bounce: bool):
    wallet_abi = Abi.from_json_path(
        path=os.path.join(SAMPLES_DIR, 'Wallet.abi.json'))
    keypair = KeyPair.load(
        path=os.path.join(SAMPLES_DIR, 'keys_wallet.json'), is_binary=False)
    signer = Signer.from_keypair(keypair=keypair)
    call_set = CallSet(
        function_name='sendTransaction',
        inputs={'dest': address, 'value': 1000000000, 'bounce': bounce})

    message_source = MessageSource.from_encoding_params(
        abi=wallet_abi, signer=signer, address=WALLET_ADDRESS,
        call_set=call_set)
    async_core_client.processing.process_message(
        message=message_source, send_events=False)
