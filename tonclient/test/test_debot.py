import asyncio
import base64
import json
import os
import unittest
import logging
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context
from typing import List, Dict, Tuple, Any, Union

from tonclient.client import TonClient
from tonclient.objects import AppDebotBrowser
from tonclient.test.helpers import SAMPLES_DIR, async_custom_client, \
    send_grams, CUSTOM_BASE_URL
from tonclient.types import Abi, Signer, CallSet, DeploySet, DebotAction, \
    DebotState, ParamsOfAppDebotBrowser, \
    ParamsOfEncodeMessage, ParamsOfProcessMessage, ParamsOfStart, \
    ParamsOfExecute, KeyPair, ParamsOfQueryCollection, ParamsOfParse, \
    ParamsOfDecodeMessageBody, ParamsOfSend, ParamsOfEncodeInternalMessage, \
    ParamsOfGetCodeFromTvc, ParamsOfGetBocHash, ParamsOfAggregateCollection, \
    FieldAggregation, AggregationFn, ParamsOfInit, ParamsOfRemove, \
    RegisteredDebot, ClientConfig, ResultOfAppDebotBrowser


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
        logging.info(f'[TERMINAL MESSAGE]\t{message}')
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


class DebotBrowser(object):
    debot: RegisteredDebot = None
    debots: Dict[str, RegisteredDebot] = {}
    switched: bool = False
    finished: bool = False
    logs: List[str] = []
    actions: List[DebotAction] = []
    messages: List[str] = []

    class AppDebot(AppDebotBrowser):
        def __init__(self, client: TonClient, browser: 'DebotBrowser'):
            super(DebotBrowser.AppDebot, self).__init__(client=client)
            self.browser = browser

        def perform_log(self, params: ParamsOfAppDebotBrowser.Log):
            logging.info(f'[LOG]\t{params.msg}')
            self.browser.logs.append(params.msg)

        def perform_switch(self, params: ParamsOfAppDebotBrowser.Switch):
            logging.info(f'[SWITCHED]\tFalse')

            self.browser.switched = False
            if params.context_id == DebotState.EXIT:
                self.browser.finished = True
            self.browser.actions.clear()

        def perform_switch_completed(self):
            logging.info(f'[SWITCHED]\tTrue')
            self.browser.switched = True

        def perform_show_action(
                self, params: ParamsOfAppDebotBrowser.ShowAction):
            logging.info(
                f'[ACTION]\t{len(self.browser.actions)}: '
                f'{params.action.__str__()}')

            self.browser.actions.append(params.action)

        def perform_input(self, params: ParamsOfAppDebotBrowser.Input) -> str:
            logging.info(f"[INPUT]\t{self.browser.step['inputs'][0]}")
            return self.browser.step['inputs'][0]

        def perform_get_signing_box(self) -> int:
            logging.info('[SIGNING BOX]')

            result = self.client.crypto.get_signing_box(
                params=self.browser.keypair)
            return result.handle

        def invoke_debot(
                self, params: ParamsOfAppDebotBrowser.InvokeDebot
        ) -> ResultOfAppDebotBrowser.InvokeDebot:
            """ Method is called by `dispatch` """
            with ProcessPoolExecutor(mp_context=get_context('spawn')) as pool:
                future = pool.submit(
                    self.perform_invoke_debot, client=self.client,
                    params=params, browser=self.browser)
                future.result()

            return ResultOfAppDebotBrowser.InvokeDebot()

        @staticmethod
        def perform_invoke_debot(
                client: TonClient, params: ParamsOfAppDebotBrowser.InvokeDebot,
                *args, **kwargs):
            logging.info(f'[INVOKE]\t{params.debot_addr}')

            browser = kwargs['browser']
            steps = browser.step['invokes']

            _browser = DebotBrowser(
                client=client, address=params.debot_addr, steps=steps,
                keypair=browser.keypair)
            _browser.actions = [params.action]
            _browser.init_debot()
            _browser.execute_from_state()

        def perform_send(self, params: ParamsOfAppDebotBrowser.Send):
            logging.info(f'[SEND]\t{params.message}')
            self.browser.messages.append(params.message)

        def perform_approve(
                self, params: ParamsOfAppDebotBrowser.Approve) -> bool:
            logging.info('[APPROVE]')
            return True

    def __init__(
            self, client: TonClient, address: str,
            steps: List[Dict[str, Any]] = None, keypair: KeyPair = None,
            terminal_outputs: List[str] = None):
        """
        :param client: Ton client instance to use
        :param address: DeBot address
        """
        self.client = client
        self.address = address
        self.steps = steps
        self.step = None
        self.keypair = keypair
        self.echo = Echo()
        self.terminal = Terminal(messages=terminal_outputs)

    def init_debot(self):
        app_debot_browser = DebotBrowser.AppDebot(
            client=self.client, browser=self)

        params = ParamsOfInit(address=self.address)
        self.debot = self.client.debot.init(
            params=params, callback=app_debot_browser.dispatcher)

        self.debots[self.address] = self.debot

    def execute(self):
        params = ParamsOfStart(debot_handle=self.debot.debot_handle)
        self.client.debot.start(params=params)
        self.execute_from_state()

    def execute_from_state(self):
        while not self.finished:
            self.handle_message_queue()

            if not self.steps or not len(self.steps):
                break

            # Execute test step
            self.step = self.steps.pop(0)
            action = self.actions[self.step['choice']]
            logging.info(f'[ACTION SELECTED]\t{action}')
            self.logs.clear()

            exec_params = ParamsOfExecute(
                debot_handle=self.debot.debot_handle, action=action)
            self.client.debot.execute(params=exec_params)

        for bot in self.debots.values():
            self.client.debot.remove(
                params=ParamsOfRemove(debot_handle=bot.debot_handle))

    def handle_message_queue(self):
        while len(self.messages):
            msg_opt = self.messages.pop(0)

            params_parse = ParamsOfParse(boc=msg_opt)
            parsed = self.client.boc.parse_message(params=params_parse)
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

                params_decode = ParamsOfDecodeMessageBody(
                    abi=abi, body=body, is_internal=True)
                decoded = async_custom_client.abi.decode_message_body(
                    params=params_decode)
                logging.debug(f'Request: `{decoded.name}` ({decoded.value})')

                if interface_id == INTERFACES[0]:
                    method = self.echo.methods[decoded.name]
                elif interface_id == INTERFACES[1]:
                    method = self.terminal.methods[decoded.name]
                else:
                    raise ValueError('Unsupported interface')

                func_id, kwargs = method(decoded.value)
                logging.debug(f'Response: `{func_id}` ({kwargs})')
                call_set = CallSet(function_name=hex(func_id), input=kwargs) \
                    if func_id > 0 else None
                internal = self.client.abi.encode_internal_message(
                    params=ParamsOfEncodeInternalMessage(
                        value='1000000000000000',
                        abi=Abi.Json(value=self.debot.debot_abi),
                        address=src_address, call_set=call_set))

                params_send = ParamsOfSend(
                    debot_handle=self.debot.debot_handle,
                    message=internal.message)
                self.client.debot.send(params=params_send)
            else:
                debot_fetched = self.debots.get(dest_address)
                if not debot_fetched:
                    _browser = DebotBrowser(
                        client=self.client, address=dest_address,
                        keypair=self.keypair)
                    _browser.init_debot()

                debot_fetched = self.debots[dest_address].debot_handle

                params_send = ParamsOfSend(
                    debot_handle=debot_fetched, message=msg_opt)
                self.client.debot.send(params=params_send)


class DebotBrowserAsync(object):
    debot: RegisteredDebot = None
    debots: Dict[str, RegisteredDebot] = {}
    switched: bool = False
    finished: bool = False
    logs: List[str] = []
    actions: List[DebotAction] = []
    messages: List[str] = []

    class AppDebot(AppDebotBrowser):
        def __init__(self, client: TonClient, browser: 'DebotBrowserAsync'):
            super(DebotBrowserAsync.AppDebot, self).__init__(client=client)
            self.browser = browser

        async def perform_log(self, params: ParamsOfAppDebotBrowser.Log):
            logging.info(f'[LOG]\t{params.msg}')
            self.browser.logs.append(params.msg)

        async def perform_switch(self, params: ParamsOfAppDebotBrowser.Switch):
            logging.info(f'[SWITCHED]\tFalse')

            self.browser.switched = False
            if params.context_id == DebotState.EXIT:
                self.browser.finished = True
            self.browser.actions.clear()

        async def perform_switch_completed(self):
            logging.info(f'[SWITCHED]\tTrue')
            self.browser.switched = True

        async def perform_show_action(
                self, params: ParamsOfAppDebotBrowser.ShowAction):
            logging.info(
                f'[ACTION]\t{len(self.browser.actions)}: '
                f'{params.action.__str__()}')
            self.browser.actions.append(params.action)

        async def perform_input(
                self, params: ParamsOfAppDebotBrowser.Input) -> str:
            logging.info(f"[INPUT]\t{self.browser.step['inputs'][0]}")
            return self.browser.step['inputs'][0]

        async def perform_get_signing_box(self) -> int:
            logging.info('[SIGNING BOX]')
            result = await self.client.crypto.get_signing_box(
                params=self.browser.keypair)
            return result.handle

        def invoke_debot(
                self, params: ParamsOfAppDebotBrowser.InvokeDebot
        ) -> ResultOfAppDebotBrowser.InvokeDebot:
            """ Method is called by `dispatch` """
            with ProcessPoolExecutor(mp_context=get_context('spawn')) as pool:
                loop = asyncio.new_event_loop()
                future = loop.run_in_executor(
                    pool, self.perform_invoke_debot, self.client, params,
                    self.browser)
                loop.run_until_complete(future)
                loop.close()

            return ResultOfAppDebotBrowser.InvokeDebot()

        @staticmethod
        def perform_invoke_debot(
                client: TonClient, params: ParamsOfAppDebotBrowser.InvokeDebot,
                *args, **kwargs):
            logging.info(f'[INVOKE]\t{params.debot_addr}')

            async def async_wrapper():
                # Create new client instance for spawned process and
                # destroy after invoke processed
                _client = TonClient(config=client.config, is_async=True)

                _browser = DebotBrowserAsync(
                    client=_client, address=params.debot_addr, steps=steps,
                    keypair=browser.keypair)
                _browser.actions = [params.action]
                await _browser.init_debot()
                await _browser.execute_from_state()

                _client.destroy_context()

            browser, = args
            steps = browser.step['invokes']

            asyncio.run(async_wrapper())

        async def perform_send(self, params: ParamsOfAppDebotBrowser.Send):
            logging.info(f'[SEND]\t{params.message}')
            self.browser.messages.append(params.message)

        async def perform_approve(
                self, params: ParamsOfAppDebotBrowser.Approve) -> bool:
            logging.info('[APPROVE]')
            return True

    def __init__(
            self, client: TonClient, address: str,
            steps: List[Dict[str, Any]] = None, keypair: KeyPair = None,
            terminal_outputs: List[str] = None):
        """
        :param client: Ton client instance to use
        :param address: DeBot address
        """
        self.client = client
        self.address = address
        self.steps = steps
        self.step = None
        self.keypair = keypair
        self.echo = Echo()
        self.terminal = Terminal(messages=terminal_outputs)

    async def init_debot(self):
        app_debot_browser = DebotBrowserAsync.AppDebot(
            client=self.client, browser=self)

        params = ParamsOfInit(address=self.address)
        self.debot = await self.client.debot.init(
            params=params, callback=app_debot_browser.dispatcher)

        self.debots[self.address] = self.debot

    async def execute(self):
        params = ParamsOfStart(debot_handle=self.debot.debot_handle)
        await self.client.debot.start(params=params)
        await self.execute_from_state()

    async def execute_from_state(self):
        while not self.finished:
            await self.handle_message_queue()

            if not self.steps or not len(self.steps):
                break

            # Execute test step
            self.step = self.steps.pop(0)
            action = self.actions[self.step['choice']]
            logging.info(f'[ACTION SELECTED]\t{action}')
            self.logs.clear()

            exec_params = ParamsOfExecute(
                debot_handle=self.debot.debot_handle, action=action)
            await self.client.debot.execute(params=exec_params)

        for bot in self.debots.values():
            await self.client.debot.remove(
                params=ParamsOfRemove(debot_handle=bot.debot_handle))

    async def handle_message_queue(self):
        while len(self.messages):
            msg_opt = self.messages.pop(0)

            params_parse = ParamsOfParse(boc=msg_opt)
            parsed = await self.client.boc.parse_message(params=params_parse)
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

                params_decode = ParamsOfDecodeMessageBody(
                    abi=abi, body=body, is_internal=True)
                decoded = await self.client.abi.decode_message_body(
                    params=params_decode)
                logging.debug(f'Request: `{decoded.name}` ({decoded.value})')

                if interface_id == INTERFACES[0]:
                    method = self.echo.methods[decoded.name]
                elif interface_id == INTERFACES[1]:
                    method = self.terminal.methods[decoded.name]
                else:
                    raise ValueError('Unsupported interface')

                func_id, kwargs = method(decoded.value)
                logging.debug(f'Response: `{func_id}` ({kwargs})')
                call_set = CallSet(function_name=hex(func_id), input=kwargs) \
                    if func_id > 0 else None
                internal = await self.client.abi.encode_internal_message(
                    params=ParamsOfEncodeInternalMessage(
                        value='1000000000000000',
                        abi=Abi.Json(value=self.debot.debot_abi),
                        address=src_address, call_set=call_set))

                params_send = ParamsOfSend(
                    debot_handle=self.debot.debot_handle,
                    message=internal.message)
                await self.client.debot.send(params=params_send)
            else:
                debot_fetched = self.debots.get(dest_address)
                if not debot_fetched:
                    _browser = DebotBrowserAsync(
                        client=self.client, address=dest_address,
                        keypair=self.keypair)
                    await _browser.init_debot()
                    debot_fetched = _browser.debot
                    self.debots[dest_address] = debot_fetched

                params_send = ParamsOfSend(
                    debot_handle=debot_fetched.debot_handle, message=msg_opt)
                await self.client.debot.send(params=params_send)


class TestTonDebotAsyncCore(unittest.TestCase):
    def setUp(self) -> None:
        self.keypair = async_custom_client.crypto.generate_random_sign_keys()
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

        browser = DebotBrowser(
            client=async_custom_client, address=debot_address, steps=steps)
        browser.init_debot()
        browser.execute()

    def test_print(self):
        debot_address, target_address = self.__init_debot(keypair=self.keypair)
        steps = [
            {
                'choice': 1,
                'inputs': [],
                'outputs': [
                    'Test Print Action',
                    'test2: instant print',
                    'test instant print'
                ]
            },
            {'choice': 0, 'inputs': [], 'outputs': ['test simple print']},
            {
                'choice': 1,
                'inputs': [],
                'outputs': [
                    f'integer=1,addr={target_address},string=test_string_1'
                ]
            },
            {'choice': 2, 'inputs': [], 'outputs': ['Debot Tests']},
            {'choice': 8, 'inputs': [], 'outputs': []}
        ]

        browser = DebotBrowser(
            client=async_custom_client, address=debot_address, steps=steps)
        browser.init_debot()
        browser.execute()

    def test_run_action(self):
        debot_address, _ = self.__init_debot(keypair=self.keypair)
        steps = [
            {'choice': 2, 'inputs': [], 'outputs': ['Test Run Action']},
            {
                'choice': 0,
                'inputs': [
                    '-1:1111111111111111111111111111111111111111111111111111111111111111'
                ],
                'outputs': [
                    'Test Instant Run',
                    'test1: instant run 1',
                    'test2: instant run 2'
                ]
            },
            {'choice': 0, 'inputs': [], 'outputs': ['Test Run Action']},
            {'choice': 1, 'inputs': ['hello'], 'outputs': []},
            {
                'choice': 2,
                'inputs': [],
                'outputs': [
                    'integer=2,addr=-1:1111111111111111111111111111111111111111111111111111111111111111,string=hello'
                ]
            },
            {'choice': 3, 'inputs': [], 'outputs': ['Debot Tests']},
            {'choice': 8, 'inputs': [], 'outputs': []}
        ]

        browser = DebotBrowser(
            client=async_custom_client, address=debot_address, steps=steps)
        browser.init_debot()
        browser.execute()

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

        browser = DebotBrowser(
            client=async_custom_client, address=debot_address, steps=steps)
        browser.init_debot()
        browser.execute()

    def test_send_message(self):
        debot_address, _ = self.__init_debot(keypair=self.keypair)
        steps = [
            {'choice': 4, 'inputs': [], 'outputs': ['Test Send Msg Action']},
            {
                'choice': 0,
                'inputs': [],
                'outputs': ['Sending message {}', 'Transaction succeeded.']
            },
            {'choice': 1, 'inputs': [], 'outputs': []},
            {'choice': 2, 'inputs': [], 'outputs': ['data=100']},
            {'choice': 3, 'inputs': [], 'outputs': ['Debot Tests']},
            {'choice': 8, 'inputs': [], 'outputs': []}
        ]

        browser = DebotBrowser(
            client=async_custom_client, address=debot_address, steps=steps,
            keypair=self.keypair)
        browser.init_debot()
        browser.execute()

    def test_invoke(self):
        debot_address, _ = self.__init_debot(keypair=self.keypair)
        steps = [
            {
                'choice': 5,
                'inputs': [debot_address],
                'outputs': ['Test Invoke Debot Action', 'enter debot address:']
            },
            {
                'choice': 0,
                'inputs': [debot_address],
                'outputs': [
                    'Test Invoke Debot Action',
                    'enter debot address:'
                ],
                'invokes': [
                    {
                        'choice': 0,
                        'inputs': [],
                        'outputs': ['Print test string', 'Debot is invoked']
                    },
                    {
                        'choice': 0,
                        'inputs': [],
                        'outputs': [
                            'Sending message {}',
                            'Transaction succeeded.'
                        ]
                    }
                ]
            },
            {'choice': 1, 'inputs': [], 'outputs': ['Debot Tests']},
            {'choice': 8, 'inputs': [], 'outputs': []}
        ]

        browser = DebotBrowser(
            client=async_custom_client, address=debot_address, steps=steps,
            keypair=self.keypair)
        browser.init_debot()
        browser.execute()

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

        browser = DebotBrowser(
            client=async_custom_client, address=debot_address, steps=steps)
        browser.init_debot()
        browser.execute()

    def test_interface_calls(self):
        debot_address, _ = self.__init_debot(keypair=self.keypair)
        steps = [
            {
                'choice': 7,
                'inputs': [],
                'outputs': ['', 'test1 - call interface']
            },
            {'choice': 0, 'inputs': [], 'outputs': ['Debot Tests']},
            {'choice': 8, 'inputs': [], 'outputs': []},
        ]

        browser = DebotBrowser(
            client=async_custom_client, address=debot_address, steps=steps)
        browser.init_debot()
        browser.execute()

    def test_debot_msg_interface(self):
        keypair = async_custom_client.crypto.generate_random_sign_keys()
        debot_address = self.__init_debot2(keypair=keypair)
        terminal_outputs = [
            'counter=10',
            'Increment succeeded',
            'counter=15'
        ]

        browser = DebotBrowser(
            client=async_custom_client, address=debot_address,
            terminal_outputs=terminal_outputs)
        browser.init_debot()
        browser.execute()

    def test_debot_sdk_interface(self):
        keypair = async_custom_client.crypto.generate_random_sign_keys()
        debot_address = self.__init_debot3(keypair=keypair)
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

        browser = DebotBrowser(
            client=async_custom_client, address=debot_address,
            terminal_outputs=terminal_outputs)
        browser.init_debot()
        browser.execute()

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
        terminal_outputs = [
            'Target contract deployed.',
            'Enter 1',
            'getData',
            'setData(128)',
            'Sign external message:',
            'Transaction succeeded',
            'setData2(129)'
        ]

        browser = DebotBrowser(
            client=async_custom_client, address=debot_address,
            terminal_outputs=terminal_outputs, keypair=keypair)
        browser.init_debot()
        browser.execute()

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
        terminal_outputs = [
            'Invoking Debot B',
            'DebotB receives question: What is your name?',
            'DebotA receives answer: My name is DebotB'
        ]

        browser = DebotBrowser(
            client=async_custom_client, address=debot_a,
            terminal_outputs=terminal_outputs)
        browser.init_debot()
        browser.execute()

    def test_debot_sdk_get_accounts_by_hash(self):
        count = 2
        addresses, contract_hash = self.__init_debot5(count=count)

        # Get contracts with hash count
        params = ParamsOfAggregateCollection(
            collection='accounts', filter={'code_hash': {'eq': contract_hash}},
            fields=[FieldAggregation(field='', fn=AggregationFn.COUNT)])
        result = async_custom_client.net.aggregate_collection(params=params)
        exists = int(result.values[0])

        # Run debot
        terminal_outputs = [f'{exists} contracts.']
        browser = DebotBrowser(
            client=async_custom_client, address=addresses[0],
            terminal_outputs=terminal_outputs)
        browser.init_debot()
        browser.execute()

    def test_debot_json_interface(self):
        keypair = async_custom_client.crypto.generate_random_sign_keys()
        debot_address = self.__init_debot7(keypair=keypair)

        browser = DebotBrowser(
            client=async_custom_client, address=debot_address)
        browser.init_debot()
        browser.execute()

    def test_invoke_async(self):
        client_config = ClientConfig()
        client_config.network.server_address = CUSTOM_BASE_URL
        client = TonClient(config=client_config, is_async=True)

        debot_address, _ = self.__init_debot(keypair=self.keypair)
        steps = [
            {
                'choice': 5,
                'inputs': [debot_address],
                'outputs': ['Test Invoke Debot Action', 'enter debot address:']
            },
            {
                'choice': 0,
                'inputs': [debot_address],
                'outputs': [
                    'Test Invoke Debot Action',
                    'enter debot address:'
                ],
                'invokes': [
                    {
                        'choice': 0,
                        'inputs': [],
                        'outputs': ['Print test string', 'Debot is invoked']
                    },
                    {
                        'choice': 0,
                        'inputs': [],
                        'outputs': [
                            'Sending message {}',
                            'Transaction succeeded.'
                        ]
                    }
                ]
            },
            {'choice': 1, 'inputs': [], 'outputs': ['Debot Tests']},
            {'choice': 8, 'inputs': [], 'outputs': []}
        ]

        async def __main():
            browser = DebotBrowserAsync(
                client=client, address=debot_address, steps=steps,
                keypair=self.keypair)
            await browser.init_debot()
            await browser.execute()

        asyncio.run(__main())

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
