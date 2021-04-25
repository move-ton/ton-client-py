import base64
import json
import os
import unittest
import logging
from multiprocessing import get_context
from concurrent.futures.thread import ThreadPoolExecutor
from typing import List, Dict, Tuple, Any, Union

from tonclient.bindings.types import TCResponseType
from tonclient.test.helpers import SAMPLES_DIR, async_custom_client, send_grams
from tonclient.types import Abi, Signer, CallSet, DeploySet, DebotAction, \
    DebotState, AppRequestResult, ParamsOfAppDebotBrowser, \
    ResultOfAppDebotBrowser, ParamsOfEncodeMessage, ParamsOfProcessMessage, \
    ParamsOfStart, ParamsOfExecute, ParamsOfAppRequest, \
    ParamsOfResolveAppRequest, KeyPair, ParamsOfQueryCollection, \
    ParamsOfParse, ParamsOfDecodeMessageBody, ParamsOfSend, \
    ParamsOfEncodeInternalMessage, ParamsOfGetCodeFromTvc, ParamsOfGetBocHash,\
    ParamsOfAggregateCollection, FieldAggregation, AggregationFn, \
    ParamsOfInit, ParamsOfRemove

DEBOT_WC = -31

INTERFACES = [
    # Echo
    'f6927c0d4bdb69e1b52d27f018d156ff04152f00558042ff674f0fec32e4369d',
    # Terminal
    '8796536366ee21852db56dccb60bc564598b618c865fc50c8b1ab740bba128e3'
]

ECHO_ABI = {
    'ABI version': 2,
    'header': ['time'],
    'functions': [
        {
            'name': 'echo',
            'inputs': [
                {'name': 'answerId', 'type': 'uint32'},
                {'name': 'request', 'type': 'bytes'}
            ],
            'outputs': [
                {'name': 'response', 'type': 'bytes'}
            ]
        }
    ],
    'data': [],
    'events': []
}

TERMINAL_ABI = {
    'ABI version': 2,
    'header': ['time'],
    'functions': [
        {
            'name': 'print',
            'inputs': [
                {'name': 'answerId', 'type': 'uint32'},
                {'name': 'message', 'type': 'bytes'}
            ],
            'outputs': []
        },
        {
            'name': 'inputInt',
            'inputs': [
                {'name': 'answerId', 'type': 'uint32'},
                {'name': 'prompt', 'type': 'bytes'}
            ],
            'outputs': [
                {'name': 'value', 'type': 'int256'}
            ]
        }
    ],
    'data': [],
    'events': []
}


class Echo(object):
    def __init__(self):
        self.methods = {
            'echo': self.echo
        }

    @staticmethod
    def echo(kwargs) -> Tuple[int, Dict[str, Any]]:
        answer_id = int(kwargs['answerId'])
        request = bytes.fromhex(kwargs['request']).decode()

        return answer_id, {'response': request.encode().hex()}


class Terminal(object):
    def __init__(self, messages: List[str]):
        self.messages = messages
        self.methods = {
            'print': self.print,
            'inputInt': self.input_int
        }
        self.test_case = unittest.TestCase()

    def print(self, kwargs: Dict[str, str]) -> Tuple[int, Dict[str, Any]]:
        answer_id = int(kwargs['answerId'])
        message = bytes.fromhex(kwargs['message']).decode()
        self.test_case.assertGreater(
            len(self.messages), 0,
            f'Terminal.messages list is empty but must contain `{message}`')
        self.test_case.assertEqual(
            self.messages.pop(0), message, 'Terminal.print assert')

        return answer_id, {}

    def input_int(self, kwargs) -> Tuple[int, Dict[str, Any]]:
        kwargs['message'] = kwargs['prompt']
        answer_id, _ = self.print(kwargs=kwargs)
        # Use test return value here
        return answer_id, {'value': 1}


class TestTonDebotAsyncCore(unittest.TestCase):
    def setUp(self) -> None:
        self.keypair = KeyPair.load(
            path=os.path.join(SAMPLES_DIR, 'keys_raw.json'), is_binary=False)
        self.target_abi = Abi.from_path(
            path=os.path.join(SAMPLES_DIR, 'DebotTarget.abi.json'))
        with open(os.path.join(SAMPLES_DIR, 'DebotTarget.tvc'), 'rb') as fp:
            self.target_tvc = base64.b64encode(fp.read()).decode()

    def test_goto(self):
        debot_address, _ = self.__init_debot(keypair=self.keypair)
        steps = [
            {'choice': 0, 'inputs': [], 'outputs': ['Test Goto Action']},
            {'choice': 0, 'inputs': [], 'outputs': ['Debot Tests']},
            {'choice': 8, 'inputs': [], 'outputs': []}
        ]
        params = ParamsOfInit(address=debot_address)
        debot_browser(
            steps=steps, params=params, start=True, keypair=self.keypair)

    def test_print(self):
        debot_address, target_address = self.__init_debot(keypair=self.keypair)
        steps = [
            {'choice': 1, 'inputs': [], 'outputs': ['Test Print Action', 'test2: instant print', 'test instant print']},
            {'choice': 0, 'inputs': [], 'outputs': ['test simple print']},
            {'choice': 1, 'inputs': [], 'outputs': [f'integer=1,addr={target_address},string=test_string_1']},
            {'choice': 2, 'inputs': [], 'outputs': ['Debot Tests']},
            {'choice': 8, 'inputs': [], 'outputs': []}
        ]
        params = ParamsOfInit(address=debot_address)
        debot_browser(
            steps=steps, params=params, start=True, keypair=self.keypair)

    def test_run_action(self):
        debot_address, _ = self.__init_debot(keypair=self.keypair)
        steps = [
            {'choice': 2, 'inputs': [], 'outputs': ['Test Run Action']},
            {'choice': 0, 'inputs': ['-1:1111111111111111111111111111111111111111111111111111111111111111'], 'outputs': ['Test Instant Run', 'test1: instant run 1', 'test2: instant run 2']},
            {'choice': 0, 'inputs': [], 'outputs': ['Test Run Action']},
            {'choice': 1, 'inputs': ['hello'], 'outputs': []},
            {'choice': 2, 'inputs': [], 'outputs': ['integer=2,addr=-1:1111111111111111111111111111111111111111111111111111111111111111,string=hello']},
            {'choice': 3, 'inputs': [], 'outputs': ['Debot Tests']},
            {'choice': 8, 'inputs': [], 'outputs': []}
        ]
        params = ParamsOfInit(address=debot_address)
        debot_browser(
            steps=steps, params=params, start=True, keypair=self.keypair)

    def test_run_method(self):
        keypair = async_custom_client.crypto.generate_random_sign_keys()
        debot_address, target_address = self.__init_debot(keypair=keypair)

        steps = [
            {'choice': 3, 'inputs': [], 'outputs': ['Test Run Method Action']},
            {'choice': 0, 'inputs': [], 'outputs': []},
            {'choice': 1, 'inputs': [], 'outputs': ['data=64']},
            {'choice': 2, 'inputs': [], 'outputs': ['Debot Tests']},
            {'choice': 8, 'inputs': [], 'outputs': []}
        ]
        params = ParamsOfInit(address=debot_address)
        debot_browser(
            steps=steps, params=params, start=True, keypair=keypair)

    def test_send_message(self):
        debot_address, _ = self.__init_debot(keypair=self.keypair)
        steps = [
            {'choice': 4, 'inputs': [], 'outputs': ['Test Send Msg Action']},
            {'choice': 0, 'inputs': [], 'outputs': ['Sending message {}', 'Transaction succeeded.']},
            {'choice': 1, 'inputs': [], 'outputs': []},
            {'choice': 2, 'inputs': [], 'outputs': ['data=100']},
            {'choice': 3, 'inputs': [], 'outputs': ['Debot Tests']},
            {'choice': 8, 'inputs': [], 'outputs': []}
        ]
        params = ParamsOfInit(address=debot_address)
        debot_browser(
            steps=steps, params=params, start=True, keypair=self.keypair)

    def test_invoke(self):
        debot_address, _ = self.__init_debot(keypair=self.keypair)
        steps = [
            {'choice': 5, 'inputs': [debot_address], 'outputs': ['Test Invoke Debot Action', 'enter debot address:']},
            {'choice': 0, 'inputs': [debot_address], 'outputs': ['Test Invoke Debot Action', 'enter debot address:'], 'invokes': [
                {'choice': 0, 'inputs': [], 'outputs': ['Print test string', 'Debot is invoked']},
                {'choice': 0, 'inputs': [], 'outputs': ['Sending message {}', 'Transaction succeeded.']}
            ]},
            {'choice': 1, 'inputs': [], 'outputs': ['Debot Tests']},
            {'choice': 8, 'inputs': [], 'outputs': []}
        ]
        params = ParamsOfInit(address=debot_address)
        debot_browser(
            steps=steps, params=params, start=True, keypair=self.keypair)

    def test_engine_calls(self):
        debot_address, _ = self.__init_debot(keypair=self.keypair)
        steps = [
            {'choice': 6, 'inputs': [], 'outputs': ['Test Engine Calls']},
            {'choice': 0, 'inputs': [], 'outputs': []},
            {'choice': 1, 'inputs': [], 'outputs': []},
            # {'choice': 2, 'inputs': [], 'outputs': []},
            {'choice': 3, 'inputs': [], 'outputs': []},
            {'choice': 4, 'inputs': [], 'outputs': []},
            {'choice': 5, 'inputs': [], 'outputs': ['Debot Tests']},
            {'choice': 8, 'inputs': [], 'outputs': []}
        ]
        params = ParamsOfInit(address=debot_address)
        debot_browser(
            steps=steps, params=params, start=True, keypair=self.keypair)

    def test_interface_calls(self):
        debot_address, _ = self.__init_debot(keypair=self.keypair)
        steps = [
            {'choice': 7, 'inputs': [], 'outputs': ['', 'test1 - call interface']},
            {'choice': 0, 'inputs': [], 'outputs': ['Debot Tests']},
            {'choice': 8, 'inputs': [], 'outputs': []},
        ]
        params = ParamsOfInit(address=debot_address)
        debot_browser(
            steps=steps, params=params, start=True, keypair=self.keypair)

    def test_debot_msg_interface(self):
        keypair = async_custom_client.crypto.generate_random_sign_keys()
        debot_address = self.__init_debot2(keypair=keypair)
        params = ParamsOfInit(address=debot_address)
        terminal_outputs = [
            'counter=10',
            'Increment succeeded',
            'counter=15'
        ]
        debot_browser(
            steps=[], params=params, start=True, keypair=keypair,
            terminal_outputs=terminal_outputs)

    def test_debot_sdk_interface(self):
        keypair = async_custom_client.crypto.generate_random_sign_keys()
        debot_address = self.__init_debot3(keypair=keypair)
        params = ParamsOfInit(address=debot_address)
        terminal_outputs = [
            'test substring1 passed',
            'test substring2 passed',
            'test mnemonicDeriveSignKeys passed',
            'test genRandom passed',
            'test naclbox passed',
            'test naclKeypairFromSecret passed',
            'test hex encode passed',
            'test base64 encode passed',
            'test mnemonic passed',
            'test naclboxopen passed',
            'test account passed',
            'test hdkeyXprv passed',
            'test hex decode passed',
            'test base64 decode passed'
        ]
        debot_browser(
            steps=[], params=params, start=True, keypair=keypair,
            terminal_outputs=terminal_outputs)

    def test_debot4(self):
        keypair = async_custom_client.crypto.generate_random_sign_keys()
        debot_address, target_address = self.__init_debot4(keypair=keypair)

        # Check target address type
        target_boc = self.download_account(address=target_address)
        self.assertIsNotNone(target_boc)
        account = async_custom_client.boc.parse_account(
            params=ParamsOfParse(boc=target_boc))
        self.assertEqual(0, account.parsed['acc_type'])

        # Run debot
        params = ParamsOfInit(address=debot_address)
        terminal_outputs = [
            'Target contract deployed.',
            'Enter 1',
            'getData',
            'setData(128)',
            'Sign external message:',
            'Transaction succeeded',
            'setData2(129)'
        ]
        debot_browser(
            steps=[], params=params, start=True, keypair=keypair,
            terminal_outputs=terminal_outputs)

        # Check address type again
        target_boc = self.download_account(address=target_address)
        self.assertIsNotNone(target_boc)
        account = async_custom_client.boc.parse_account(
            params=ParamsOfParse(boc=target_boc))
        self.assertEqual(1, account.parsed['acc_type'])

    def test_debot_invoke_msgs(self):
        keypair = async_custom_client.crypto.generate_random_sign_keys()
        debot_a, _ = self.__init_debot_pair(keypair=keypair)

        # Run debot
        params = ParamsOfInit(address=debot_a)
        terminal_outputs = [
            'Invoking Debot B',
            'DebotB receives question: What is your name?',
            'DebotA receives answer: My name is DebotB'
        ]
        debot_browser(
            steps=[], params=params, start=True, keypair=keypair,
            terminal_outputs=terminal_outputs)

    def test_debot_sdk_get_accounts_by_hash(self):
        count = 2
        keypair = async_custom_client.crypto.generate_random_sign_keys()
        addresses, contract_hash = self.__init_debot5(count=count)

        # Get contracts with hash count
        params = ParamsOfAggregateCollection(
            collection='accounts', filter={'code_hash': {'eq': contract_hash}},
            fields=[FieldAggregation(field='', fn=AggregationFn.COUNT)])
        result = async_custom_client.net.aggregate_collection(params=params)
        exists = int(result.values[0])

        # Run debot
        params = ParamsOfInit(address=addresses[0])
        terminal_outputs = [
            f'{exists} contracts.'
        ]
        debot_browser(
            steps=[], params=params, start=True, keypair=keypair,
            terminal_outputs=terminal_outputs)

    def test_debot_json_interface(self):
        keypair = async_custom_client.crypto.generate_random_sign_keys()
        debot_address = self.__init_debot7(keypair=keypair)
        params = ParamsOfInit(address=debot_address)
        terminal_outputs = []
        debot_browser(
            steps=[], params=params, start=True, keypair=keypair,
            terminal_outputs=terminal_outputs)

    @staticmethod
    def debot_print_state(state: Dict[str, Any]):
        # Print messages
        for message in state['messages']:
            logging.info(f'[LOG]\t{message}')
        # Print available actions
        for action in state['actions']:
            logging.info(f'[ACTION]\t{action}')

    def __init_debot(self, keypair: KeyPair) -> Tuple[str, str]:
        """ Deploy debot and target """
        signer = Signer.Keys(keys=keypair)
        debot_abi = Abi.from_path(
            path=os.path.join(SAMPLES_DIR, 'Debot.abi.json'))
        with open(os.path.join(SAMPLES_DIR, 'Debot.tvc'), 'rb') as fp:
            debot_tvc = base64.b64encode(fp.read()).decode()

        # Deploy target
        call_set = CallSet(function_name='constructor')
        deploy_set = DeploySet(tvc=self.target_tvc)
        encode_params = ParamsOfEncodeMessage(
            abi=self.target_abi, signer=signer, deploy_set=deploy_set,
            call_set=call_set)
        message = async_custom_client.abi.encode_message(params=encode_params)

        # Check if target contract does not exists
        target_address = self.__check_address(address=message.address)
        if not target_address:
            process_params = ParamsOfProcessMessage(
                message_encode_params=encode_params, send_events=False)
            target = async_custom_client.processing.process_message(
                params=process_params)
            target_address = target.transaction['account_addr']

        # Deploy debot
        call_set = CallSet(
            function_name='constructor', input={
                'targetAbi': self.target_abi.value.encode().hex(),
                'targetAddr': target_address
            })
        deploy_set = DeploySet(tvc=debot_tvc)
        encode_params = ParamsOfEncodeMessage(
            abi=debot_abi, signer=signer, deploy_set=deploy_set,
            call_set=call_set)
        message = async_custom_client.abi.encode_message(params=encode_params)

        # Check if debot contract does not exists
        debot_address = self.__check_address(address=message.address)
        if not debot_address:
            process_params = ParamsOfProcessMessage(
                message_encode_params=encode_params, send_events=False)
            debot = async_custom_client.processing.process_message(
                params=process_params)
            debot_address = debot.transaction['account_addr']

            # Set ABI
            call_set = CallSet(
                function_name='setAbi',
                input={'debotAbi': debot_abi.value.encode().hex()})
            async_custom_client.processing.process_message(
                params=ParamsOfProcessMessage(
                    message_encode_params=ParamsOfEncodeMessage(
                        abi=debot_abi, signer=Signer.NoSigner(),
                        address=debot_address, call_set=call_set),
                    send_events=False))

        return debot_address, target_address

    def __init_debot2(self, keypair: KeyPair) -> str:
        signer = Signer.Keys(keys=keypair)
        debot_abi = Abi.from_path(
            path=os.path.join(SAMPLES_DIR, 'Debot2.abi.json'))
        with open(os.path.join(SAMPLES_DIR, 'Debot2.tvc'), 'rb') as fp:
            debot_tvc = base64.b64encode(fp.read()).decode()

        call_set = CallSet(
            function_name='constructor',
            input={
                'pub': f'0x{keypair.public}',
                'sec': f'0x{keypair.secret}'
            })
        deploy_set = DeploySet(tvc=debot_tvc)
        encode_params = ParamsOfEncodeMessage(
            abi=debot_abi, signer=signer, deploy_set=deploy_set,
            call_set=call_set)
        message = async_custom_client.abi.encode_message(params=encode_params)

        # Check if debot contract does not exists
        debot_address = self.__check_address(address=message.address)
        if not debot_address:
            process_params = ParamsOfProcessMessage(
                message_encode_params=encode_params, send_events=False)
            debot = async_custom_client.processing.process_message(
                params=process_params)
            debot_address = debot.transaction['account_addr']

            # Set ABI
            call_set = CallSet(
                function_name='setAbi',
                input={'debotAbi': debot_abi.value.encode().hex()})
            async_custom_client.processing.process_message(
                params=ParamsOfProcessMessage(
                    message_encode_params=ParamsOfEncodeMessage(
                        abi=debot_abi, signer=signer, address=debot_address,
                        call_set=call_set),
                    send_events=False))

        return debot_address

    def __init_debot3(self, keypair: KeyPair) -> str:
        return self.__init_simple_debot(name='Debot3', keypair=keypair)

    def __init_debot4(self, keypair: KeyPair) -> Tuple[str, str]:
        signer = Signer.Keys(keys=keypair)
        debot_abi = Abi.from_path(
            path=os.path.join(SAMPLES_DIR, 'Debot4.abi.json'))
        with open(os.path.join(SAMPLES_DIR, 'Debot4.tvc'), 'rb') as fp:
            debot_tvc = base64.b64encode(fp.read()).decode()

        # Init target
        call_set = CallSet(function_name='constructor')
        deploy_set = DeploySet(tvc=self.target_tvc)
        encode_params = ParamsOfEncodeMessage(
            abi=self.target_abi, signer=signer, deploy_set=deploy_set,
            call_set=call_set)
        message = async_custom_client.abi.encode_message(params=encode_params)
        target_address = message.address
        self.__check_address(address=target_address)

        # Deploy debot
        call_set = CallSet(
            function_name='constructor', input={
                'targetAbi': self.target_abi.value.encode().hex(),
                'targetAddr': target_address
            })
        deploy_set = DeploySet(tvc=debot_tvc)
        encode_params = ParamsOfEncodeMessage(
            abi=debot_abi, signer=signer, deploy_set=deploy_set,
            call_set=call_set)
        message = async_custom_client.abi.encode_message(params=encode_params)

        # Check if debot contract does not exists
        debot_address = self.__check_address(address=message.address)
        if not debot_address:
            process_params = ParamsOfProcessMessage(
                message_encode_params=encode_params, send_events=False)
            debot = async_custom_client.processing.process_message(
                params=process_params)
            debot_address = debot.transaction['account_addr']

            # Set ABI
            call_set = CallSet(
                function_name='setAbi',
                input={'debotAbi': debot_abi.value.encode().hex()})
            async_custom_client.processing.process_message(
                params=ParamsOfProcessMessage(
                    message_encode_params=ParamsOfEncodeMessage(
                        abi=debot_abi, signer=signer, address=debot_address,
                        call_set=call_set),
                    send_events=False))

            # Set image
            call_set = CallSet(
                function_name='setImage',
                input={
                    'image': self.target_tvc,
                    'pubkey': f'0x{keypair.public}'
                })
            async_custom_client.processing.process_message(
                params=ParamsOfProcessMessage(
                    message_encode_params=ParamsOfEncodeMessage(
                        abi=debot_abi, signer=signer, address=debot_address,
                        call_set=call_set),
                    send_events=False))

        return debot_address, target_address

    def __init_debot5(self, count: int) -> Tuple[List[str], str]:
        debot_abi = Abi.from_path(
            path=os.path.join(SAMPLES_DIR, 'Debot5.abi.json'))
        with open(os.path.join(SAMPLES_DIR, 'Debot5.tvc'), 'rb') as fp:
            debot_tvc = base64.b64encode(fp.read()).decode()

        result = async_custom_client.boc.get_code_from_tvc(
            params=ParamsOfGetCodeFromTvc(tvc=debot_tvc))
        result = async_custom_client.boc.get_boc_hash(
            params=ParamsOfGetBocHash(boc=result.code))
        contract_hash = result.hash

        call_set = CallSet(
            function_name='constructor',
            input={'codeHash': f'0x{contract_hash}'})
        deploy_set = DeploySet(tvc=debot_tvc)
        deploy_params = ParamsOfEncodeMessage(
            abi=debot_abi, deploy_set=deploy_set, call_set=call_set,
            signer=Signer.NoSigner())

        addresses = []
        for i in range(count):
            # Set signer for deploy params
            keypair = async_custom_client.crypto.generate_random_sign_keys()
            deploy_params.signer = Signer.Keys(keys=keypair)

            # Calculate address
            message = async_custom_client.abi.encode_message(
                params=deploy_params)
            self.__check_address(address=message.address)

            # Deploy address
            process_params = ParamsOfProcessMessage(
                message_encode_params=deploy_params, send_events=False)
            result = async_custom_client.processing.process_message(
                params=process_params)
            debot_address = result.transaction['account_addr']
            addresses.append(debot_address)
            if i > 0:
                continue

            # Set ABI
            call_set = CallSet(
                function_name='setABI',
                input={'dabi': debot_abi.value.encode().hex()})
            async_custom_client.processing.process_message(
                params=ParamsOfProcessMessage(
                    message_encode_params=ParamsOfEncodeMessage(
                        abi=debot_abi, signer=deploy_params.signer,
                        address=debot_address, call_set=call_set),
                    send_events=False))

        return addresses, contract_hash

    def __init_debot7(self, keypair: KeyPair) -> str:
        return self.__init_simple_debot(name='Debot7', keypair=keypair)

    def __init_debot_pair(self, keypair: KeyPair) -> Tuple[str, str]:
        signer = Signer.Keys(keys=keypair)
        debot_a_abi = Abi.from_path(
            path=os.path.join(SAMPLES_DIR, 'DebotPairA.abi.json'))
        with open(os.path.join(SAMPLES_DIR, 'DebotPairA.tvc'), 'rb') as fp:
            debot_a_tvc = base64.b64encode(fp.read()).decode()

        debot_b_abi = Abi.from_path(
            path=os.path.join(SAMPLES_DIR, 'DebotPairB.abi.json'))
        with open(os.path.join(SAMPLES_DIR, 'DebotPairB.tvc'), 'rb') as fp:
            debot_b_tvc = base64.b64encode(fp.read()).decode()

        # Deploy debot B
        call_set = CallSet(function_name='constructor')
        deploy_set = DeploySet(tvc=debot_b_tvc)
        encode_params = ParamsOfEncodeMessage(
            abi=debot_b_abi, signer=signer, deploy_set=deploy_set,
            call_set=call_set)
        message = async_custom_client.abi.encode_message(params=encode_params)
        b_address = message.address

        self.__check_address(address=b_address)
        process_params = ParamsOfProcessMessage(
            message_encode_params=encode_params, send_events=False)
        debot_b = async_custom_client.processing.process_message(
            params=process_params)
        b_address = debot_b.transaction['account_addr']

        # Set ABI
        call_set = CallSet(
            function_name='setAbi',
            input={'debotAbi': debot_b_abi.value.encode().hex()})
        async_custom_client.processing.process_message(
            params=ParamsOfProcessMessage(
                message_encode_params=ParamsOfEncodeMessage(
                    abi=debot_b_abi, signer=signer, address=b_address,
                    call_set=call_set),
                send_events=False))

        # Deploy debot A
        call_set = CallSet(
            function_name='constructor', input={
                'targetAddr': b_address
            })
        deploy_set = DeploySet(tvc=debot_a_tvc)
        encode_params = ParamsOfEncodeMessage(
            abi=debot_a_abi, signer=signer, deploy_set=deploy_set,
            call_set=call_set)
        message = async_custom_client.abi.encode_message(params=encode_params)
        a_address = message.address

        self.__check_address(address=a_address)
        process_params = ParamsOfProcessMessage(
            message_encode_params=encode_params, send_events=False)
        debot_a = async_custom_client.processing.process_message(
            params=process_params)
        a_address = debot_a.transaction['account_addr']

        # Set ABI
        call_set = CallSet(
            function_name='setAbi',
            input={'debotAbi': debot_a_abi.value.encode().hex()})
        async_custom_client.processing.process_message(
            params=ParamsOfProcessMessage(
                message_encode_params=ParamsOfEncodeMessage(
                    abi=debot_a_abi, signer=signer, address=a_address,
                    call_set=call_set),
                send_events=False))

        return a_address, b_address

    def __init_simple_debot(self, name: str, keypair: KeyPair) -> str:
        """ Common method to init simple DeBots """

        signer = Signer.Keys(keys=keypair)
        debot_abi = Abi.from_path(
            path=os.path.join(SAMPLES_DIR, f'{name}.abi.json'))
        with open(os.path.join(SAMPLES_DIR, f'{name}.tvc'), 'rb') as fp:
            debot_tvc = base64.b64encode(fp.read()).decode()

        call_set = CallSet(function_name='constructor')
        deploy_set = DeploySet(tvc=debot_tvc)
        encode_params = ParamsOfEncodeMessage(
            abi=debot_abi, signer=signer, deploy_set=deploy_set,
            call_set=call_set)
        message = async_custom_client.abi.encode_message(params=encode_params)

        # Check if debot contract does not exists
        debot_address = self.__check_address(address=message.address)
        if not debot_address:
            process_params = ParamsOfProcessMessage(
                message_encode_params=encode_params, send_events=False)
            debot = async_custom_client.processing.process_message(
                params=process_params)
            debot_address = debot.transaction['account_addr']

            # Set ABI
            call_set = CallSet(
                function_name='setABI',
                input={'dabi': debot_abi.value.encode().hex()})
            async_custom_client.processing.process_message(
                params=ParamsOfProcessMessage(
                    message_encode_params=ParamsOfEncodeMessage(
                        abi=debot_abi, signer=signer, address=debot_address,
                        call_set=call_set),
                    send_events=False))

        return debot_address

    @staticmethod
    def __check_address(address: str) -> Union[str, None]:
        """ Check if address exists or `send_grams` """
        q_params = ParamsOfQueryCollection(
            collection='accounts', result='id',
            filter={'id': {'eq': address}})
        result = async_custom_client.net.query_collection(params=q_params)
        if len(result.result):
            return result.result[0]['id']

        send_grams(address=address)

    @staticmethod
    def download_account(address: str) -> Union[str, None]:
        accounts = async_custom_client.net.query_collection(
            params=ParamsOfQueryCollection(
                collection='accounts', result='boc',
                filter={'id': {'eq': address}}, limit=1))
        if len(accounts.result):
            return accounts.result[0]['boc']

        return None


def debot_browser(
        steps: List[Dict[str, Any]], start: bool, keypair: KeyPair,
        params: ParamsOfInit, state: Dict[str, Any] = None,
        actions: List[DebotAction] = None, terminal_outputs: List[str] = None):

    def __callback(response_data, response_type, *args):
        # Process notifications
        if response_type == TCResponseType.AppNotify:
            notify = ParamsOfAppDebotBrowser.from_dict(data=response_data)

            # Process notification types
            if isinstance(notify, ParamsOfAppDebotBrowser.Log):
                state['messages'].append(notify.msg)
            if isinstance(notify, ParamsOfAppDebotBrowser.Switch):
                state['switch_started'] = True
                if notify.context_id == DebotState.EXIT:
                    state['finished'] = True
                state['actions'].clear()
            if isinstance(
                    notify, ParamsOfAppDebotBrowser.SwitchCompleted):
                state['switch_started'] = False
            if isinstance(notify, ParamsOfAppDebotBrowser.ShowAction):
                state['actions'].append(notify.action)
            if isinstance(notify, ParamsOfAppDebotBrowser.Send):
                state['msg_queue'].append(notify.message)

        # Process requests
        if response_type == TCResponseType.AppRequest:
            request = ParamsOfAppRequest(**response_data)
            request_data = ParamsOfAppDebotBrowser.from_dict(
                data=request.request_data)
            result = None

            # Process request types
            if isinstance(request_data, ParamsOfAppDebotBrowser.Input):
                result = ResultOfAppDebotBrowser.Input(
                    value=state['step']['inputs'][0])
            if isinstance(
                    request_data, ParamsOfAppDebotBrowser.GetSigningBox):
                with ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        async_custom_client.crypto.get_signing_box,
                        params=keypair)
                    signing_box = future.result()
                result = ResultOfAppDebotBrowser.GetSigningBox(
                    signing_box=signing_box.handle)
            if isinstance(
                    request_data, ParamsOfAppDebotBrowser.InvokeDebot):
                invoke_steps = state['step']['invokes']
                _params = ParamsOfInit(address=request_data.debot_addr)

                # Here we should call `debot_browser` in `spawn` mode
                # subprocess for compatibility with `Unix` systems.
                # MacOS, Windows use `spawn` by default
                with get_context('spawn').Pool() as pool:
                    pool.apply(debot_browser, kwds={
                        'steps': invoke_steps,
                        'params': _params,
                        'start': False,
                        'actions': [request_data.action],
                        'keypair': keypair
                    })
                result = ResultOfAppDebotBrowser.InvokeDebot()
            if isinstance(request_data, ParamsOfAppDebotBrowser.Approve):
                result = ResultOfAppDebotBrowser.Approve(approved=True)

            # Resolve app request
            result = AppRequestResult.Ok(result=result.dict)
            resolve_params = ParamsOfResolveAppRequest(
                app_request_id=request.app_request_id, result=result)
            with ThreadPoolExecutor() as executor:
                future = executor.submit(
                    async_custom_client.resolve_app_request,
                    params=resolve_params)
                future.result()

    def __handle_message_queue():
        while len(state['msg_queue']):
            msg_opt = state['msg_queue'].pop(0)

            parsed = async_custom_client.boc.parse_message(
                params=ParamsOfParse(boc=msg_opt))
            body = parsed.parsed['body']
            dest_address = parsed.parsed['dst']
            src_address = parsed.parsed['src']
            wc, interface_id = dest_address.split(':')

            if wc == str(DEBOT_WC):
                if interface_id == INTERFACES[0]:
                    abi = Abi.Json(value=json.dumps(ECHO_ABI))
                elif interface_id == INTERFACES[1]:
                    abi = Abi.Json(value=json.dumps(TERMINAL_ABI))
                else:
                    raise ValueError('Unsupported interface')

                decoded = async_custom_client.abi.decode_message_body(
                    params=ParamsOfDecodeMessageBody(
                        abi=abi, body=body, is_internal=True))
                logging.info(f'Request: `{decoded.name}` ({decoded.value})')

                if interface_id == INTERFACES[0]:
                    method = state['echo'].methods[decoded.name]
                elif interface_id == INTERFACES[1]:
                    method = state['terminal'].methods[decoded.name]
                else:
                    raise ValueError('Unsupported interface')

                func_id, kwargs = method(decoded.value)
                logging.info(f'Response: `{func_id}` ({kwargs})')
                call_set = CallSet(function_name=hex(func_id), input=kwargs) \
                    if func_id > 0 else None
                internal = async_custom_client.abi.encode_internal_message(
                    params=ParamsOfEncodeInternalMessage(
                        value='1000000000000000',
                        abi=Abi.Json(value=debot.debot_abi),
                        address=src_address, call_set=call_set))
                async_custom_client.debot.send(
                    params=ParamsOfSend(
                        debot_handle=debot.debot_handle,
                        message=internal.message))
            else:
                debot_fetched = state['bots'].get(dest_address)
                if not debot_fetched:
                    _params = ParamsOfInit(address=dest_address)
                    debot_browser(
                        steps=[], start=False, keypair=keypair,
                        params=_params, state=state)

                debot_fetched = state['bots'][dest_address].debot_handle
                async_custom_client.debot.send(
                    params=ParamsOfSend(
                        debot_handle=debot_fetched, message=msg_opt))

    # Create initial state
    test_case = unittest.TestCase()  # For unit tests only
    if not state:
        state: Dict[str, Any] = {
            'messages': [],
            'actions': actions or [],
            'steps': steps,
            'step': None,
            'switch_started': False,
            'finished': False,
            'msg_queue': [],
            'terminal': Terminal(messages=terminal_outputs),
            'echo': Echo(),
            'bots': {}
        }

    # Start debot browser and get handle
    debot = async_custom_client.debot.init(params=params, callback=__callback)
    state['bots'][params.address] = debot
    if start:
        async_custom_client.debot.start(
            params=ParamsOfStart(debot_handle=debot.debot_handle))
    TestTonDebotAsyncCore.debot_print_state(state=state)

    while not state['finished']:
        __handle_message_queue()

        if not len(state['steps']):
            break
        step: Dict[str, Any] = state['steps'].pop(0)
        action = state['actions'][step['choice']]
        logging.info(f'[ACTION SELECTED]\t{action}')
        state['messages'].clear()
        state['step'] = step

        exec_params = ParamsOfExecute(
            debot_handle=debot.debot_handle, action=action)
        async_custom_client.debot.execute(params=exec_params)
        TestTonDebotAsyncCore.debot_print_state(state=state)

        test_case.assertEqual(
            len(state['step']['outputs']), len(state['messages']))

    if start:
        for bot in state['bots'].values():
            async_custom_client.debot.remove(
                params=ParamsOfRemove(debot_handle=bot.debot_handle))
