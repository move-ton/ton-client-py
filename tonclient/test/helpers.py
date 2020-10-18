import os

from tonclient.client import TonClient, DEVNET_BASE_URL
from tonclient.net import TonQLQuery
from tonclient.types import Abi, CallSet, Signer, MessageSource, \
    ExecutionMode
from tonclient.types import KeyPair

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


def get_giver(address: str):
    wallet_abi = Abi.from_json_path(
        path=os.path.join(SAMPLES_DIR, 'Giver.abi.json'))
    keypair = KeyPair.load(
        path=os.path.join(SAMPLES_DIR, 'keys_wallet.json'), is_binary=False)
    signer = Signer.from_keypair(keypair=keypair)
    call_set = CallSet(
        function_name='grant',
        inputs={'addr': address})
    query = TonQLQuery(collection='accounts') \
        .set_filter(id__eq="0:653b9a6452c7a982c6dc92b2da9eba832ade1c467699ebb3b43dca6d77b780dd") \
        .set_result('id boc')
    account = async_core_client.net.wait_for_collection(query=query)
    # MessageSource.from_encoded()
    message_source = MessageSource.from_encoding_params(
        abi=wallet_abi, signer=signer, address="0:653b9a6452c7a982c6dc92b2da9eba832ade1c467699ebb3b43dca6d77b780dd",
        call_set=call_set)
    # async_core_client.processing.
    # async_core_client.processing.send_message(call_set.dict,send_events=False,abi=wallet_abi)
    # sync_core_client.net.request("contracts.run",address="0:653b9a6452c7a982c6dc92b2da9eba832ade1c467699ebb3b43dca6d77b780dd",abi=wallet_abi.dict,functionName="grant",inputs={'addr': address})
    async_core_client.tvm.execute_message(
        message=message_source, mode=ExecutionMode.Full, account=account["boc"])


get_giver(WALLET_ADDRESS)
