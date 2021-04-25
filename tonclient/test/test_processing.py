import base64
import logging
import os
import unittest

from tonclient.errors import TonException
from tonclient.test.test_abi import SAMPLES_DIR
from tonclient.test.helpers import send_grams, async_custom_client
from tonclient.types import Abi, DeploySet, CallSet, Signer, FunctionHeader, \
    ParamsOfEncodeMessage, ParamsOfProcessMessage, ProcessingResponseType, \
    ProcessingEvent, ParamsOfSendMessage, ParamsOfWaitForTransaction


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
        signer = Signer.Keys(keys=keypair)
        call_set = CallSet(
            function_name='constructor',
            header=FunctionHeader(pubkey=keypair.public))
        # Encode deployment message
        encode_params = ParamsOfEncodeMessage(
            abi=self.events_abi, signer=signer, deploy_set=self.deploy_set,
            call_set=call_set)
        encoded = async_custom_client.abi.encode_message(params=encode_params)

        # Send grams
        send_grams(address=encoded.address)

        # Deploy account
        process_params = ParamsOfProcessMessage(
            message_encode_params=encode_params, send_events=False)
        result = async_custom_client.processing.process_message(
            params=process_params)

        self.assertEqual(
            encoded.address, result.transaction['account_addr'])
        self.assertEqual('finalized', result.transaction['status_name'])
        self.assertEqual(0, len(result.out_messages))

        # Contract execution error
        with self.assertRaises(TonException):
            call_set = CallSet(function_name='returnValue', input={'id': -1})
            encode_params = ParamsOfEncodeMessage(
                abi=self.events_abi, signer=signer, address=encoded.address,
                call_set=call_set)
            process_params = ParamsOfProcessMessage(
                message_encode_params=encode_params, send_events=False)

            async_custom_client.processing.process_message(
                params=process_params)

    def test_process_message_with_events(self):
        # Prepare data for deployment message
        keypair = async_custom_client.crypto.generate_random_sign_keys()
        signer = Signer.Keys(keys=keypair)
        call_set = CallSet(
            function_name='constructor',
            header=FunctionHeader(pubkey=keypair.public))
        # Encode deployment message
        encode_params = ParamsOfEncodeMessage(
            abi=self.events_abi, signer=signer, deploy_set=self.deploy_set,
            call_set=call_set)
        encoded = async_custom_client.abi.encode_message(params=encode_params)

        # Send grams
        send_grams(address=encoded.address)

        # Deploy account
        events = []

        def __callback(response_data, response_type, *args):
            self.assertEqual(
                ProcessingResponseType.PROCESSING_EVENT, response_type)
            event = ProcessingEvent.from_dict(data=response_data)
            events.append(event)

        deploy_params = ParamsOfProcessMessage(
            message_encode_params=encode_params, send_events=True)
        deploy = async_custom_client.processing.process_message(
            params=deploy_params, callback=__callback)

        self.assertEqual(
            encoded.address, deploy.transaction['account_addr'])
        self.assertEqual('finalized', deploy.transaction['status_name'])
        self.assertEqual(0, len(deploy.out_messages))

        logging.info('Events fired')
        for e in events:
            logging.info(e.type)

    def test_wait_for_transaction(self):
        # Create deploy message
        keypair = async_custom_client.crypto.generate_random_sign_keys()
        signer = Signer.Keys(keys=keypair)
        call_set = CallSet(
            function_name='constructor',
            header=FunctionHeader(pubkey=keypair.public))
        encode_params = ParamsOfEncodeMessage(
            abi=self.events_abi, signer=signer, deploy_set=self.deploy_set,
            call_set=call_set)
        encoded = async_custom_client.abi.encode_message(params=encode_params)

        # Send grams
        send_grams(address=encoded.address)

        # Send message
        send_params = ParamsOfSendMessage(
            message=encoded.message, send_events=False, abi=self.events_abi)
        send = async_custom_client.processing.send_message(
            params=send_params)

        # Wait for transaction
        wait_params = ParamsOfWaitForTransaction(
            message=encoded.message, shard_block_id=send.shard_block_id,
            send_events=False, abi=self.events_abi,
            sending_endpoints=send.sending_endpoints)
        wait = async_custom_client.processing.wait_for_transaction(
            params=wait_params)
        self.assertEqual([], wait.out_messages)
        self.assertEqual([], wait.decoded.out_messages)
        self.assertIsNone(wait.decoded.output)

    def test_wait_for_transaction_with_events(self):
        # Create deploy message
        keypair = async_custom_client.crypto.generate_random_sign_keys()
        signer = Signer.Keys(keys=keypair)
        call_set = CallSet(
            function_name='constructor',
            header=FunctionHeader(pubkey=keypair.public))
        encode_params = ParamsOfEncodeMessage(
            abi=self.events_abi, signer=signer, deploy_set=self.deploy_set,
            call_set=call_set)
        encoded = async_custom_client.abi.encode_message(params=encode_params)

        # Send grams
        send_grams(address=encoded.address)

        # Send message
        events = []

        def __callback(response_data, response_type, *args):
            self.assertEqual(
                ProcessingResponseType.PROCESSING_EVENT, response_type)
            event = ProcessingEvent.from_dict(data=response_data)
            events.append(event)

        send_params = ParamsOfSendMessage(
            message=encoded.message, send_events=True, abi=self.events_abi)
        send = async_custom_client.processing.send_message(
            params=send_params, callback=__callback)

        logging.info('Send message events:')
        for e in events:
            logging.info(e.type)
        logging.info(f'Shard block id: {send.shard_block_id}')

        # Wait for transaction
        events.clear()
        wait_params = ParamsOfWaitForTransaction(
            message=encoded.message, shard_block_id=send.shard_block_id,
            send_events=True, abi=self.events_abi,
            sending_endpoints=send.sending_endpoints)
        wait = async_custom_client.processing.wait_for_transaction(
            params=wait_params, callback=__callback)

        self.assertEqual([], wait.out_messages)
        self.assertEqual([], wait.decoded.out_messages)
        self.assertIsNone(wait.decoded.output)

        logging.info('Wait message events:')
        for e in events:
            logging.info(e.type)
