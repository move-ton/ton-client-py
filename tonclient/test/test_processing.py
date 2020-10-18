import base64
import os
import unittest

from tonclient.test.test_abi import SAMPLES_DIR
from tonclient.test.helpers import send_grams, async_core_client
from tonclient.types import Abi, DeploySet, CallSet, Signer, MessageSource


class TestTonProcessingAsyncCore(unittest.TestCase):
    def setUp(self) -> None:
        self.events_abi = Abi.from_json_path(
            path=os.path.join(SAMPLES_DIR, 'Events.abi.json'))
        with open(os.path.join(SAMPLES_DIR, 'Events.tvc'), 'rb') as fp:
            self.events_tvc = base64.b64encode(fp.read()).decode()
        self.deploy_set = DeploySet(tvc=self.events_tvc)

    def test_process_message(self):
        # Prepare data for deployment message
        events_abi = Abi.from_json_path(
            path=os.path.join(SAMPLES_DIR, 'Events.abi.json'))
        keypair = async_core_client.crypto.generate_random_sign_keys()
        signer = Signer.from_keypair(keypair=keypair)
        call_set = CallSet(
            function_name='constructor', header={'pubkey': keypair.public})
        # Encode deployment message
        encoded = async_core_client.abi.encode_message(
            abi=self.events_abi, signer=signer,
            deploy_set=self.deploy_set, call_set=call_set)

        # Send grams
        send_grams(address=encoded['address'], bounce=False)

        # Deploy account
        message_source = MessageSource.from_encoded(
            message=encoded['message'], abi=events_abi)
        result = async_core_client.processing.process_message(
            message=message_source, send_events=False)

        self.assertEqual([], result['out_messages'])
        self.assertEqual(
            {'out_messages': [], 'output': None}, result['decoded'])

    def test_wait_for_transaction(self):
        # Create deploy message
        keypair = async_core_client.crypto.generate_random_sign_keys()
        signer = Signer.from_keypair(keypair=keypair)
        call_set = CallSet(
            function_name='constructor', header={'pubkey': keypair.public})
        encoded = async_core_client.abi.encode_message(
            abi=self.events_abi, signer=signer,
            deploy_set=self.deploy_set, call_set=call_set)

        # Send grams
        send_grams(address=encoded['address'], bounce=False)

        # Send message
        shard_block_id = async_core_client.processing.send_message(
            message=encoded['message'], send_events=False, abi=self.events_abi)

        # Wait for transaction
        result = async_core_client.processing.wait_for_transaction(
            message=encoded['message'], shard_block_id=shard_block_id,
            send_events=False, abi=self.events_abi)
        self.assertEqual([], result['out_messages'])
        self.assertEqual(
            {'out_messages': [], 'output': None}, result['decoded'])
