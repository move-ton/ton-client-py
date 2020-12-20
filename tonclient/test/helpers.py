import os

from tonclient.client import TonClient, DEVNET_BASE_URL
from tonclient.types import Abi, CallSet, Signer, ClientConfig, \
    ParamsOfEncodeMessage, ParamsOfProcessMessage

BASE_DIR = os.path.dirname(__file__)
SAMPLES_DIR = os.path.join(BASE_DIR, 'samples')
GIVER_ADDRESS = '0:f5c2510bfe407363cb1db6b9d7bc1184a05f8b343aeaa828189c580e8569ee23'
CUSTOM_BASE_URL = 'https://tonos.freeton.surf'

client_config = ClientConfig()
client_config.network.server_address = DEVNET_BASE_URL
async_core_client = TonClient(config=client_config)
sync_core_client = TonClient(config=client_config, is_core_async=False)

client_config.network.server_address = CUSTOM_BASE_URL
async_custom_client = TonClient(config=client_config)


def send_grams(address: str):
    giver_abi = Abi.from_path(
        path=os.path.join(SAMPLES_DIR, 'Giver.abi.json'))
    call_set = CallSet(
        function_name='grant', input={'dest': address})
    encode_params = ParamsOfEncodeMessage(
        abi=giver_abi, signer=Signer.NoSigner(), address=GIVER_ADDRESS,
        call_set=call_set)
    process_params = ParamsOfProcessMessage(
        message_encode_params=encode_params, send_events=False)
    async_custom_client.processing.process_message(params=process_params)
