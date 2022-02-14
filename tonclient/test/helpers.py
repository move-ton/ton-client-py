import os

from tonclient.client import TonClient
from tonclient.types import (
    Abi,
    CallSet,
    Signer,
    ClientConfig,
    ParamsOfEncodeMessage,
    ParamsOfProcessMessage,
)

BASE_DIR = os.path.dirname(__file__)
SAMPLES_DIR = os.path.join(BASE_DIR, 'samples')
GIVER_ADDRESS = '0:f5c2510bfe407363cb1db6b9d7bc1184a05f8b343aeaa828189c580e8569ee23'

client_config = ClientConfig()
client_config.network.endpoints = ['https://everos.freeton.surf']
async_core_client = TonClient(config=client_config)
sync_core_client = TonClient(config=client_config, is_core_async=False)


def send_grams(address: str):
    """Helper to send tokens from giver"""
    giver_abi = Abi.from_path(path=os.path.join(SAMPLES_DIR, 'Giver.abi.json'))
    call_set = CallSet(function_name='grant', input={'dest': address})
    encode_params = ParamsOfEncodeMessage(
        abi=giver_abi,
        signer=Signer.NoSigner(),
        address=GIVER_ADDRESS,
        call_set=call_set,
    )
    process_params = ParamsOfProcessMessage(
        message_encode_params=encode_params, send_events=False
    )
    async_core_client.processing.process_message(params=process_params)


def tonos_punch():
    """Produce transaction for local node"""
    send_grams(
        address='0:b5e9240fc2d2f1ff8cbb1d1dee7fb7cae155e5f6320e585fcc685698994a19a5'
    )
