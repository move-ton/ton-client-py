import os

from tonclient.client import TonClient, DEVNET_BASE_URL
from tonclient.types import Abi, CallSet, Signer

BASE_DIR = os.path.dirname(__file__)
SAMPLES_DIR = os.path.join(BASE_DIR, 'samples')
GIVER_ADDRESS = '0:653b9a6452c7a982c6dc92b2da9eba832ade1c467699ebb3b43dca6d77b780dd'

async_core_client = TonClient(network={'server_address': DEVNET_BASE_URL})
sync_core_client = TonClient(
    network={'server_address': DEVNET_BASE_URL}, is_core_async=False)


def send_grams(address: str):
    giver_abi = Abi.from_json_path(
        path=os.path.join(SAMPLES_DIR, 'Giver.abi.json'))
    call_set = CallSet(
        function_name='grant',
        inputs={'addr': address})
    async_core_client.processing.process_message(
        abi=giver_abi, signer=Signer.none(), address=GIVER_ADDRESS,
        call_set=call_set, send_events=False)
