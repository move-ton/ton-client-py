import base64
import logging
import os
import unittest
import time

from tonclient.errors import TonException
from tonclient.test.test_abi import SAMPLES_DIR
from tonclient.test.helpers import send_grams, async_core_client, sync_core_client
from tonclient.types import (
    Abi,
    DeploySet,
    CallSet,
    MessageMonitoringParams,
    MessageSendingParams,
    MonitoredMessage,
    ParamsOfCancelMonitor,
    ParamsOfGetBocHash,
    ParamsOfGetMonitorInfo,
    ParamsOfMonitorMessages,
    ParamsOfSendMessages,
    Signer,
    FunctionHeader,
    ParamsOfEncodeMessage,
    ParamsOfProcessMessage,
    ProcessingResponseType,
    ProcessingEvent,
    ParamsOfSendMessage,
    ParamsOfWaitForTransaction,
)


class TestTonProcessingAsyncCore(unittest.TestCase):
    def setUp(self) -> None:
        self.events_abi = Abi.from_path(
            path=os.path.join(SAMPLES_DIR, 'Events.abi.json')
        )
        with open(os.path.join(SAMPLES_DIR, 'Events.tvc'), 'rb') as fp:
            self.events_tvc = base64.b64encode(fp.read()).decode()
        self.deploy_set = DeploySet(tvc=self.events_tvc)

    def test_process_message(self):
        # Prepare data for deployment message
        keypair = async_core_client.crypto.generate_random_sign_keys()
        signer = Signer.Keys(keys=keypair)
        call_set = CallSet(
            function_name='constructor', header=FunctionHeader(pubkey=keypair.public)
        )
        # Encode deployment message
        encode_params = ParamsOfEncodeMessage(
            abi=self.events_abi,
            signer=signer,
            deploy_set=self.deploy_set,
            call_set=call_set,
        )
        encoded = async_core_client.abi.encode_message(params=encode_params)

        # Send grams
        send_grams(address=encoded.address)

        # Deploy account
        process_params = ParamsOfProcessMessage(
            message_encode_params=encode_params, send_events=False
        )
        result = async_core_client.processing.process_message(params=process_params)

        self.assertEqual(encoded.address, result.transaction['account_addr'])
        self.assertEqual('finalized', result.transaction['status_name'])
        self.assertEqual(0, len(result.out_messages))

        # Contract execution error
        with self.assertRaises(TonException):
            call_set = CallSet(function_name='returnValue', input={'id': -1})
            encode_params = ParamsOfEncodeMessage(
                abi=self.events_abi,
                signer=signer,
                address=encoded.address,
                call_set=call_set,
            )
            process_params = ParamsOfProcessMessage(
                message_encode_params=encode_params, send_events=False
            )

            async_core_client.processing.process_message(params=process_params)

    def test_process_message_with_events(self):
        # Prepare data for deployment message
        keypair = async_core_client.crypto.generate_random_sign_keys()
        signer = Signer.Keys(keys=keypair)
        call_set = CallSet(
            function_name='constructor', header=FunctionHeader(pubkey=keypair.public)
        )
        # Encode deployment message
        encode_params = ParamsOfEncodeMessage(
            abi=self.events_abi,
            signer=signer,
            deploy_set=self.deploy_set,
            call_set=call_set,
        )
        encoded = async_core_client.abi.encode_message(params=encode_params)

        # Send grams
        send_grams(address=encoded.address)

        # Deploy account
        events = []

        def __callback(response_data, response_type, *args):
            self.assertEqual(ProcessingResponseType.PROCESSING_EVENT, response_type)
            event = ProcessingEvent.from_dict(data=response_data)
            events.append(event)

        deploy_params = ParamsOfProcessMessage(
            message_encode_params=encode_params, send_events=True
        )
        deploy = async_core_client.processing.process_message(
            params=deploy_params, callback=__callback
        )

        self.assertEqual(encoded.address, deploy.transaction['account_addr'])
        self.assertEqual('finalized', deploy.transaction['status_name'])
        self.assertEqual(0, len(deploy.out_messages))

        logging.info('Events fired')
        for e in events:
            logging.info(e.type)

    def test_wait_for_transaction(self):
        # Create deploy message
        keypair = async_core_client.crypto.generate_random_sign_keys()
        signer = Signer.Keys(keys=keypair)
        call_set = CallSet(
            function_name='constructor', header=FunctionHeader(pubkey=keypair.public)
        )
        encode_params = ParamsOfEncodeMessage(
            abi=self.events_abi,
            signer=signer,
            deploy_set=self.deploy_set,
            call_set=call_set,
        )
        encoded = async_core_client.abi.encode_message(params=encode_params)

        # Send grams
        send_grams(address=encoded.address)

        # Send message
        send_params = ParamsOfSendMessage(
            message=encoded.message, send_events=False, abi=self.events_abi
        )
        send = async_core_client.processing.send_message(params=send_params)

        # Wait for transaction
        wait_params = ParamsOfWaitForTransaction(
            message=encoded.message,
            shard_block_id=send.shard_block_id,
            send_events=False,
            abi=self.events_abi,
            sending_endpoints=send.sending_endpoints,
        )
        wait = async_core_client.processing.wait_for_transaction(params=wait_params)
        self.assertEqual([], wait.out_messages)
        self.assertEqual([], wait.decoded.out_messages)
        self.assertIsNone(wait.decoded.output)

    def test_wait_for_transaction_with_events(self):
        # Create deploy message
        keypair = async_core_client.crypto.generate_random_sign_keys()
        signer = Signer.Keys(keys=keypair)
        call_set = CallSet(
            function_name='constructor', header=FunctionHeader(pubkey=keypair.public)
        )
        encode_params = ParamsOfEncodeMessage(
            abi=self.events_abi,
            signer=signer,
            deploy_set=self.deploy_set,
            call_set=call_set,
        )
        encoded = async_core_client.abi.encode_message(params=encode_params)

        # Send grams
        send_grams(address=encoded.address)

        # Send message
        events = []

        def __callback(response_data, response_type, *args):
            self.assertEqual(ProcessingResponseType.PROCESSING_EVENT, response_type)
            event = ProcessingEvent.from_dict(data=response_data)
            events.append(event)

        send_params = ParamsOfSendMessage(
            message=encoded.message, send_events=True, abi=self.events_abi
        )
        send = async_core_client.processing.send_message(
            params=send_params, callback=__callback
        )

        logging.info('Send message events:')
        for e in events:
            logging.info(e.type)
        logging.info(f'Shard block id: {send.shard_block_id}')

        # Wait for transaction
        events.clear()
        wait_params = ParamsOfWaitForTransaction(
            message=encoded.message,
            shard_block_id=send.shard_block_id,
            send_events=True,
            abi=self.events_abi,
            sending_endpoints=send.sending_endpoints,
        )
        wait = async_core_client.processing.wait_for_transaction(
            params=wait_params, callback=__callback
        )

        self.assertEqual([], wait.out_messages)
        self.assertEqual([], wait.decoded.out_messages)
        self.assertIsNone(wait.decoded.output)

        logging.info('Wait message events:')
        for e in events:
            logging.info(e.type)

    def test_send_messages_monitoring(self):
        wait_until = int(time.time()) + 10

        # Create deploy messages
        messages = []
        for _ in range(5):
            keypair = async_core_client.crypto.generate_random_sign_keys()
            signer = Signer.Keys(keys=keypair)
            call_set = CallSet(
                function_name='constructor',
                header=FunctionHeader(pubkey=keypair.public),
            )
            encode_params = ParamsOfEncodeMessage(
                abi=self.events_abi,
                signer=signer,
                deploy_set=self.deploy_set,
                call_set=call_set,
            )
            encoded = async_core_client.abi.encode_message(params=encode_params)
            send_grams(address=encoded.address)
            messages.append(encoded)

        # Send messages
        queue_id = 'test-queue-1'
        params_msg = [
            MessageSendingParams(
                boc=encoded.message, wait_until=wait_until, user_data={'id': 'user_id'}
            )
            for encoded in messages
        ]
        params = ParamsOfSendMessages(messages=params_msg, monitor_queue=queue_id)
        result = async_core_client.processing.send_messages(params=params)
        self.assertEqual(5, len(result.messages))
        self.assertEqual({'id': 'user_id'}, result.messages[0].user_data)
        self.assertEqual(messages[0].message, result.messages[0].message.boc)

        # Get monitor info
        params = ParamsOfGetMonitorInfo(queue=queue_id)
        info = async_core_client.processing.get_monitor_info(params=params)
        self.assertEqual(5, info.unresolved)
        self.assertEqual(0, info.resolved)

        # Fetch next monitoring results
        # It is not supported by node SE yet
        # params = ParamsOfFetchNextMonitorResults(
        #     queue=queue_id, wait_mode=MonitorFetchWaitMode.AT_LEAST_ONE
        # )
        # result = async_core_client.processing.fetch_next_monitor_results(params=params)
        # print(result.__dict__)

        # Cancel monitor
        params = ParamsOfCancelMonitor(queue=queue_id)
        async_core_client.processing.cancel_monitor(params=params)

    def test_message_monitoring(self):
        wait_until = int(time.time()) + 10
        queue_id = 'queue-1'

        # Create deploy messages
        messages = []
        for _ in range(5):
            keypair = async_core_client.crypto.generate_random_sign_keys()
            signer = Signer.Keys(keys=keypair)
            call_set = CallSet(
                function_name='constructor',
                header=FunctionHeader(pubkey=keypair.public),
            )
            encode_params = ParamsOfEncodeMessage(
                abi=self.events_abi,
                signer=signer,
                deploy_set=self.deploy_set,
                call_set=call_set,
            )
            encoded = async_core_client.abi.encode_message(params=encode_params)
            send_grams(address=encoded.address)

            result = async_core_client.boc.get_boc_hash(
                params=ParamsOfGetBocHash(boc=encoded.message)
            )
            message = MonitoredMessage.HashAddress(
                hash=result.hash, address=encoded.address
            )
            messages.append(
                MessageMonitoringParams(message=message, wait_until=wait_until)
            )

        # Monitor messages
        params = ParamsOfMonitorMessages(queue=queue_id, messages=messages)
        async_core_client.processing.monitor_messages(params=params)

        # Fetch next monitoring results
        # It is not supported by node SE yet

        # Cancel monitor
        params = ParamsOfCancelMonitor(queue=queue_id)
        async_core_client.processing.cancel_monitor(params=params)


class TestTonProcessingSyncCore(unittest.TestCase):
    def setUp(self) -> None:
        self.events_abi = Abi.from_path(
            path=os.path.join(SAMPLES_DIR, 'Events.abi.json')
        )
        with open(os.path.join(SAMPLES_DIR, 'Events.tvc'), 'rb') as fp:
            self.events_tvc = base64.b64encode(fp.read()).decode()
        self.deploy_set = DeploySet(tvc=self.events_tvc)

    def test_process_message(self):
        # Prepare data for deployment message
        keypair = sync_core_client.crypto.generate_random_sign_keys()
        signer = Signer.Keys(keys=keypair)
        call_set = CallSet(
            function_name='constructor', header=FunctionHeader(pubkey=keypair.public)
        )
        # Encode deployment message
        encode_params = ParamsOfEncodeMessage(
            abi=self.events_abi,
            signer=signer,
            deploy_set=self.deploy_set,
            call_set=call_set,
        )
        encoded = sync_core_client.abi.encode_message(params=encode_params)

        # Send grams
        send_grams(address=encoded.address)

        # Deploy account
        process_params = ParamsOfProcessMessage(
            message_encode_params=encode_params, send_events=False
        )
        result = sync_core_client.processing.process_message(params=process_params)

        self.assertEqual(encoded.address, result.transaction['account_addr'])
        self.assertEqual('finalized', result.transaction['status_name'])
        self.assertEqual(0, len(result.out_messages))

        # Contract execution error
        with self.assertRaises(TonException):
            call_set = CallSet(function_name='returnValue', input={'id': -1})
            encode_params = ParamsOfEncodeMessage(
                abi=self.events_abi,
                signer=signer,
                address=encoded.address,
                call_set=call_set,
            )
            process_params = ParamsOfProcessMessage(
                message_encode_params=encode_params, send_events=False
            )

            sync_core_client.processing.process_message(params=process_params)

    def test_process_message_with_events(self):
        # Prepare data for deployment message
        keypair = sync_core_client.crypto.generate_random_sign_keys()
        signer = Signer.Keys(keys=keypair)
        call_set = CallSet(
            function_name='constructor', header=FunctionHeader(pubkey=keypair.public)
        )
        # Encode deployment message
        encode_params = ParamsOfEncodeMessage(
            abi=self.events_abi,
            signer=signer,
            deploy_set=self.deploy_set,
            call_set=call_set,
        )
        encoded = sync_core_client.abi.encode_message(params=encode_params)

        # Send grams
        send_grams(address=encoded.address)

        # Deploy account
        events = []

        def __callback(response_data, response_type, *args):
            self.assertEqual(ProcessingResponseType.PROCESSING_EVENT, response_type)
            event = ProcessingEvent.from_dict(data=response_data)
            events.append(event)

        deploy_params = ParamsOfProcessMessage(
            message_encode_params=encode_params, send_events=True
        )
        deploy = sync_core_client.processing.process_message(
            params=deploy_params, callback=__callback
        )

        self.assertEqual(encoded.address, deploy.transaction['account_addr'])
        self.assertEqual('finalized', deploy.transaction['status_name'])
        self.assertEqual(0, len(deploy.out_messages))

        logging.info('Events fired')
        for e in events:
            logging.info(e.type)

    def test_wait_for_transaction(self):
        # Create deploy message
        keypair = sync_core_client.crypto.generate_random_sign_keys()
        signer = Signer.Keys(keys=keypair)
        call_set = CallSet(
            function_name='constructor', header=FunctionHeader(pubkey=keypair.public)
        )
        encode_params = ParamsOfEncodeMessage(
            abi=self.events_abi,
            signer=signer,
            deploy_set=self.deploy_set,
            call_set=call_set,
        )
        encoded = sync_core_client.abi.encode_message(params=encode_params)

        # Send grams
        send_grams(address=encoded.address)

        # Send message
        send_params = ParamsOfSendMessage(
            message=encoded.message, send_events=False, abi=self.events_abi
        )
        send = sync_core_client.processing.send_message(params=send_params)

        # Wait for transaction
        wait_params = ParamsOfWaitForTransaction(
            message=encoded.message,
            shard_block_id=send.shard_block_id,
            send_events=False,
            abi=self.events_abi,
            sending_endpoints=send.sending_endpoints,
        )
        wait = sync_core_client.processing.wait_for_transaction(params=wait_params)
        self.assertEqual([], wait.out_messages)
        self.assertEqual([], wait.decoded.out_messages)
        self.assertIsNone(wait.decoded.output)

    def test_wait_for_transaction_with_events(self):
        # Create deploy message
        keypair = sync_core_client.crypto.generate_random_sign_keys()
        signer = Signer.Keys(keys=keypair)
        call_set = CallSet(
            function_name='constructor', header=FunctionHeader(pubkey=keypair.public)
        )
        encode_params = ParamsOfEncodeMessage(
            abi=self.events_abi,
            signer=signer,
            deploy_set=self.deploy_set,
            call_set=call_set,
        )
        encoded = sync_core_client.abi.encode_message(params=encode_params)

        # Send grams
        send_grams(address=encoded.address)

        # Send message
        events = []

        def __callback(response_data, response_type, *args):
            self.assertEqual(ProcessingResponseType.PROCESSING_EVENT, response_type)
            event = ProcessingEvent.from_dict(data=response_data)
            events.append(event)

        send_params = ParamsOfSendMessage(
            message=encoded.message, send_events=True, abi=self.events_abi
        )
        send = sync_core_client.processing.send_message(
            params=send_params, callback=__callback
        )

        logging.info('Send message events:')
        for e in events:
            logging.info(e.type)
        logging.info(f'Shard block id: {send.shard_block_id}')

        # Wait for transaction
        events.clear()
        wait_params = ParamsOfWaitForTransaction(
            message=encoded.message,
            shard_block_id=send.shard_block_id,
            send_events=True,
            abi=self.events_abi,
            sending_endpoints=send.sending_endpoints,
        )
        wait = sync_core_client.processing.wait_for_transaction(
            params=wait_params, callback=__callback
        )

        self.assertEqual([], wait.out_messages)
        self.assertEqual([], wait.decoded.out_messages)
        self.assertIsNone(wait.decoded.output)

        logging.info('Wait message events:')
        for e in events:
            logging.info(e.type)

    def test_send_messages_monitoring(self):
        wait_until = int(time.time()) + 10

        # Create deploy messages
        messages = []
        for _ in range(5):
            keypair = sync_core_client.crypto.generate_random_sign_keys()
            signer = Signer.Keys(keys=keypair)
            call_set = CallSet(
                function_name='constructor',
                header=FunctionHeader(pubkey=keypair.public),
            )
            encode_params = ParamsOfEncodeMessage(
                abi=self.events_abi,
                signer=signer,
                deploy_set=self.deploy_set,
                call_set=call_set,
            )
            encoded = sync_core_client.abi.encode_message(params=encode_params)
            send_grams(address=encoded.address)
            messages.append(encoded)

        # Send messages
        queue_id = 'test-queue-1'
        params_msg = [
            MessageSendingParams(
                boc=encoded.message, wait_until=wait_until, user_data={'id': 'user_id'}
            )
            for encoded in messages
        ]
        params = ParamsOfSendMessages(messages=params_msg, monitor_queue=queue_id)
        result = sync_core_client.processing.send_messages(params=params)
        self.assertEqual(5, len(result.messages))
        self.assertEqual({'id': 'user_id'}, result.messages[0].user_data)
        self.assertEqual(messages[0].message, result.messages[0].message.boc)

        # Get monitor info
        params = ParamsOfGetMonitorInfo(queue=queue_id)
        info = sync_core_client.processing.get_monitor_info(params=params)
        self.assertEqual(5, info.unresolved)
        self.assertEqual(0, info.resolved)

        # Fetch next monitoring results
        # It is not supported by node SE yet
        # params = ParamsOfFetchNextMonitorResults(
        #     queue=queue_id, wait_mode=MonitorFetchWaitMode.AT_LEAST_ONE
        # )
        # result = sync_core_client.processing.fetch_next_monitor_results(params=params)
        # print(result.__dict__)

        # Cancel monitor
        params = ParamsOfCancelMonitor(queue=queue_id)
        sync_core_client.processing.cancel_monitor(params=params)

    def test_message_monitoring(self):
        wait_until = int(time.time()) + 10
        queue_id = 'queue-1'

        # Create deploy messages
        messages = []
        for _ in range(5):
            keypair = sync_core_client.crypto.generate_random_sign_keys()
            signer = Signer.Keys(keys=keypair)
            call_set = CallSet(
                function_name='constructor',
                header=FunctionHeader(pubkey=keypair.public),
            )
            encode_params = ParamsOfEncodeMessage(
                abi=self.events_abi,
                signer=signer,
                deploy_set=self.deploy_set,
                call_set=call_set,
            )
            encoded = sync_core_client.abi.encode_message(params=encode_params)
            send_grams(address=encoded.address)

            result = sync_core_client.boc.get_boc_hash(
                params=ParamsOfGetBocHash(boc=encoded.message)
            )
            message = MonitoredMessage.HashAddress(
                hash=result.hash, address=encoded.address
            )
            messages.append(
                MessageMonitoringParams(message=message, wait_until=wait_until)
            )

        # Monitor messages
        params = ParamsOfMonitorMessages(queue=queue_id, messages=messages)
        sync_core_client.processing.monitor_messages(params=params)

        # Fetch next monitoring results
        # It is not supported by node SE yet

        # Cancel monitor
        params = ParamsOfCancelMonitor(queue=queue_id)
        sync_core_client.processing.cancel_monitor(params=params)
