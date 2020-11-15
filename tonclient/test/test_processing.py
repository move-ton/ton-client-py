import base64
import logging
import os
import unittest

from tonclient.errors import TonException
from tonclient.test.test_abi import SAMPLES_DIR
from tonclient.test.helpers import send_grams, async_custom_client
from tonclient.types import Abi, DeploySet, CallSet, Signer


class TestTonProcessingAsyncCore(unittest.TestCase):
    def setUp(self) -> None:
        self.events_abi = Abi.from_path(
            path=os.path.join(SAMPLES_DIR, 'Events.abi.json'))
        with open(os.path.join(SAMPLES_DIR, 'Events.tvc'), 'rb') as fp:
            self.events_tvc = base64.b64encode(fp.read()).decode()
        self.deploy_set = DeploySet(tvc=self.events_tvc)

    def test_process_message(self):
        # Prepare data for deployment message
        keypair = async_custom_client.crypto.generate_random_sign_keys()
        signer = Signer.from_keypair(keypair=keypair)
        call_set = CallSet(
            function_name='constructor', header={'pubkey': keypair.public})
        # Encode deployment message
        encoded = async_custom_client.abi.encode_message(
            abi=self.events_abi, signer=signer, deploy_set=self.deploy_set,
            call_set=call_set)

        # Send grams
        send_grams(address=encoded['address'])

        # Deploy account
        result = async_custom_client.processing.process_message(
            abi=self.events_abi, signer=signer, deploy_set=self.deploy_set,
            call_set=call_set, send_events=False)

        self.assertEqual(
            encoded['address'], result['transaction']['account_addr'])
        self.assertEqual('finalized', result['transaction']['status_name'])
        self.assertEqual(0, len(result['out_messages']))

        # Contract execution error
        with self.assertRaises(TonException):
            call_set = CallSet(function_name='returnValue', inputs={'id': -1})
            async_custom_client.processing.process_message(
                abi=self.events_abi, signer=signer, address=encoded['address'],
                call_set=call_set, send_events=False)

    def test_process_message_with_events(self):
        # Prepare data for deployment message
        keypair = async_custom_client.crypto.generate_random_sign_keys()
        signer = Signer.from_keypair(keypair=keypair)
        call_set = CallSet(
            function_name='constructor', header={'pubkey': keypair.public})
        # Encode deployment message
        encoded = async_custom_client.abi.encode_message(
            abi=self.events_abi, signer=signer,
            deploy_set=self.deploy_set, call_set=call_set)

        # Send grams
        send_grams(address=encoded['address'])

        # Deploy account
        generator = async_custom_client.processing.process_message(
            abi=self.events_abi, signer=signer, deploy_set=self.deploy_set,
            call_set=call_set, send_events=True)
        events = []
        for event in generator:
            data = event.get('response_data', {})
            log_message = None
            if data.get('type'):
                log_message = f"Type: '{data['type']}'; "
                if data.get('shard_block_id'):
                    log_message += f"Shard block id: '{data['shard_block_id']}'"
            elif data.get('transaction'):
                log_message = f"Transaction id: '{data['transaction']['id']}'"
            logging.info(f"[Process message event] {log_message}")

            events.append(event)

        result = events[-1]['response_data']
        self.assertEqual(
            encoded['address'], result['transaction']['account_addr'])
        self.assertEqual('finalized', result['transaction']['status_name'])
        self.assertEqual(0, len(result['out_messages']))

    def test_wait_for_transaction(self):
        # Create deploy message
        keypair = async_custom_client.crypto.generate_random_sign_keys()
        signer = Signer.from_keypair(keypair=keypair)
        call_set = CallSet(
            function_name='constructor', header={'pubkey': keypair.public})
        encoded = async_custom_client.abi.encode_message(
            abi=self.events_abi, signer=signer,
            deploy_set=self.deploy_set, call_set=call_set)

        # Send grams
        send_grams(address=encoded['address'])

        # Send message
        shard_block_id = async_custom_client.processing.send_message(
            message=encoded['message'], send_events=False, abi=self.events_abi)

        # Wait for transaction
        result = async_custom_client.processing.wait_for_transaction(
            message=encoded['message'], shard_block_id=shard_block_id,
            send_events=False, abi=self.events_abi)
        self.assertEqual([], result['out_messages'])
        self.assertEqual(
            {'out_messages': [], 'output': None}, result['decoded'])

    def test_wait_for_transaction_with_events(self):
        # Create deploy message
        keypair = async_custom_client.crypto.generate_random_sign_keys()
        signer = Signer.from_keypair(keypair=keypair)
        call_set = CallSet(
            function_name='constructor', header={'pubkey': keypair.public})
        encoded = async_custom_client.abi.encode_message(
            abi=self.events_abi, signer=signer,
            deploy_set=self.deploy_set, call_set=call_set)

        # Send grams
        send_grams(address=encoded['address'])

        # Send message
        generator = async_custom_client.processing.send_message(
            message=encoded['message'], send_events=True, abi=self.events_abi)
        events = []
        for event in generator:
            data = event.get('response_data', {})
            if type(data) is dict and data.get('type'):
                log_message = f"Type: '{data['type']}'"
            else:
                log_message = f"Shard block id: '{data}'"
            logging.info(f"[Send message event] {log_message}")

            events.append(event)
        shard_block_id = events[-1]['response_data']

        # Wait for transaction
        generator = async_custom_client.processing.wait_for_transaction(
            message=encoded['message'], shard_block_id=shard_block_id,
            send_events=True, abi=self.events_abi)
        events.clear()
        for event in generator:
            data = event.get('response_data', {})
            log_message = None
            if data.get('type'):
                log_message = f"Type: '{data['type']}'; " \
                              f"Shard block id: '{data['shard_block_id']}'"
            elif data.get('transaction'):
                log_message = f"Transaction id: '{data['transaction']['id']}'"
            logging.info(f"[Wait for transaction event] {log_message}")

            events.append(event)

        result = events[-1]['response_data']
        self.assertEqual([], result['out_messages'])
        self.assertEqual(
            {'out_messages': [], 'output': None}, result['decoded'])
