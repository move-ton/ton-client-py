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
    ParamsOfStart, ParamsOfFetch, ParamsOfExecute, ParamsOfAppRequest, \
    ParamsOfResolveAppRequest, KeyPair, ParamsOfQueryCollection, ParamsOfParse, \
    ParamsOfDecodeMessageBody, ParamsOfSend

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
        params = ParamsOfStart(address=debot_address)
        debot_browser(
            steps=steps, params=params, start_fn='start', keypair=self.keypair)

    def test_print(self):
        debot_address, target_address = self.__init_debot(keypair=self.keypair)
        steps = [
            {'choice': 1, 'inputs': [], 'outputs': ['Test Print Action', 'test2: instant print', 'test instant print']},
            {'choice': 0, 'inputs': [], 'outputs': ['test simple print']},
            {'choice': 1, 'inputs': [], 'outputs': [f'integer=1,addr={target_address},string=test_string_1']},
            {'choice': 2, 'inputs': [], 'outputs': ['Debot Tests']},
            {'choice': 8, 'inputs': [], 'outputs': []}
        ]
        params = ParamsOfStart(address=debot_address)
        debot_browser(
            steps=steps, params=params, start_fn='start', keypair=self.keypair)

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
        params = ParamsOfStart(address=debot_address)
        debot_browser(
            steps=steps, params=params, start_fn='start', keypair=self.keypair)

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
        params = ParamsOfStart(address=debot_address)
        debot_browser(
            steps=steps, params=params, start_fn='start', keypair=keypair)

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
        params = ParamsOfStart(address=debot_address)
        debot_browser(
            steps=steps, params=params, start_fn='start', keypair=self.keypair)

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
        params = ParamsOfStart(address=debot_address)
        debot_browser(
            steps=steps, params=params, start_fn='start', keypair=self.keypair)

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
        params = ParamsOfStart(address=debot_address)
        debot_browser(
            steps=steps, params=params, start_fn='start', keypair=self.keypair)

    def test_interface_calls(self):
        debot_address, _ = self.__init_debot(keypair=self.keypair)
        steps = [
            {'choice': 7, 'inputs': [], 'outputs': ['', 'test1 - call interface']},
            {'choice': 0, 'inputs': [], 'outputs': ['Debot Tests']},
            {'choice': 8, 'inputs': [], 'outputs': []},
        ]
        params = ParamsOfStart(address=debot_address)
        debot_browser(
            steps=steps, params=params, start_fn='start', keypair=self.keypair)

    def test_debot_msg_interface(self):
        keypair = async_custom_client.crypto.generate_random_sign_keys()
        debot_address = self.__init_debot2(keypair=keypair)
        params = ParamsOfStart(address=debot_address)
        terminal_outputs = [
            'counter=10',
            'Increment succeeded',
            'counter=15'
        ]
        debot_browser(
            steps=[], params=params, start_fn='start', keypair=keypair,
            terminal_outputs=terminal_outputs)

    def test_debot_sdk_interface(self):
        keypair = async_custom_client.crypto.generate_random_sign_keys()
        debot_address = self.__init_debot3(keypair=keypair)
        params = ParamsOfStart(address=debot_address)
        terminal_outputs = [
            'test substring1 passed',
            'test substring2 passed',
            'test mnemonicDeriveSignKeys passed',
            'test genRandom passed',
            'test mnemonic passed',
            'test account passed',
            'test hdkeyXprv passed'
        ]
        debot_browser(
            steps=[], params=params, start_fn='start', keypair=keypair,
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
        params = ParamsOfStart(address=debot_address)
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
            steps=[], params=params, start_fn='start', keypair=keypair,
            terminal_outputs=terminal_outputs)

        # Check address type again
        target_boc = self.download_account(address=target_address)
        self.assertIsNotNone(target_boc)
        account = async_custom_client.boc.parse_account(
            params=ParamsOfParse(boc=target_boc))
        self.assertEqual(1, account.parsed['acc_type'])

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
        signer = Signer.Keys(keys=keypair)
        debot_abi = Abi.from_path(
            path=os.path.join(SAMPLES_DIR, 'Debot3.abi.json'))
        with open(os.path.join(SAMPLES_DIR, 'Debot3.tvc'), 'rb') as fp:
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
        steps: List[Dict[str, Any]], start_fn: str, keypair: KeyPair,
        params: Union[ParamsOfStart, ParamsOfFetch],
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
                fetch_params = ParamsOfFetch(address=request_data.debot_addr)

                # Here we should call `debot_browser` in `spawn` mode
                # subprocess for compatibility with `Unix` systems.
                # MacOS, Windows use `spawn` by default
                with get_context('spawn').Pool() as pool:
                    pool.apply(debot_browser, kwds={
                        'steps': invoke_steps,
                        'params': fetch_params,
                        'start_fn': 'fetch',
                        'actions': [request_data.action],
                        'keypair': keypair
                    })
                result = ResultOfAppDebotBrowser.InvokeDebot()

            # Resolve app request
            result = AppRequestResult.Ok(result=result.dict)
            resolve_params = ParamsOfResolveAppRequest(
                app_request_id=request.app_request_id, result=result)
            with ThreadPoolExecutor() as executor:
                future = executor.submit(
                    async_custom_client.resolve_app_request,
                    params=resolve_params)
                future.result()

    def __execute_interface_calls():
        while len(state['msg_queue']):
            msg_opt = state['msg_queue'].pop(0)

            parsed = async_custom_client.boc.parse_message(
                params=ParamsOfParse(boc=msg_opt))
            body = parsed.parsed['body']
            interface_address = parsed.parsed['dst']
            wc, interface_id = interface_address.split(':')
            test_case.assertIn(interface_id, INTERFACES)

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

            async_custom_client.debot.send(
                params=ParamsOfSend(
                    debot_handle=debot.debot_handle, source=interface_address,
                    func_id=func_id, params=json.dumps(kwargs)))

    # Create initial state
    test_case = unittest.TestCase()  # For unit tests only
    state: Dict[str, Any] = {
        'messages': [],
        'actions': actions or [],
        'steps': steps,
        'step': None,
        'switch_started': False,
        'finished': False,
        'msg_queue': [],
        'terminal': Terminal(messages=terminal_outputs),
        'echo': Echo()
    }

    # Start debot browser and get handle
    debot = getattr(async_custom_client.debot, start_fn)(
        params=params, callback=__callback)
    TestTonDebotAsyncCore.debot_print_state(state=state)

    while not state['finished']:
        __execute_interface_calls()

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

    async_custom_client.debot.remove(params=debot)
