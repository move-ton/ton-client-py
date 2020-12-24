import base64
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
    ParamsOfResolveAppRequest, KeyPair, ParamsOfQueryCollection


class TestTonDebotAsyncCore(unittest.TestCase):
    def setUp(self) -> None:
        self.keypair = KeyPair.load(
            path=os.path.join(SAMPLES_DIR, 'keys_raw.json'), is_binary=False)
        self.target_abi = Abi.from_path(
            path=os.path.join(SAMPLES_DIR, 'DebotTarget.abi.json'))
        self.debot_abi = Abi.from_path(
            path=os.path.join(SAMPLES_DIR, 'Debot.abi.json'))
        with open(os.path.join(SAMPLES_DIR, 'DebotTarget.tvc'), 'rb') as fp:
            self.target_tvc = base64.b64encode(fp.read()).decode()
        with open(os.path.join(SAMPLES_DIR, 'Debot.tvc'), 'rb') as fp:
            self.debot_tvc = base64.b64encode(fp.read()).decode()

        self.debot_address, self.target_address = self.__deploy(
            keypair=self.keypair)

    def test_goto(self):
        steps = [
            {'choice': 0, 'inputs': [], 'outputs': ['Test Goto Action']},
            {'choice': 0, 'inputs': [], 'outputs': ['Debot Tests']},
            {'choice': 7, 'inputs': [], 'outputs': []}
        ]
        params = ParamsOfStart(address=self.debot_address)
        debot_browser(
            steps=steps, params=params, start_fn='start', keypair=self.keypair)

    def test_print(self):
        steps = [
            {'choice': 1, 'inputs': [], 'outputs': ['Test Print Action', 'test2: instant print', 'test instant print']},
            {'choice': 0, 'inputs': [], 'outputs': ['test simple print']},
            {'choice': 1, 'inputs': [], 'outputs': [f'integer=1,addr={self.target_address},string=test_string_1']},
            {'choice': 2, 'inputs': [], 'outputs': ['Debot Tests']},
            {'choice': 7, 'inputs': [], 'outputs': []}
        ]
        params = ParamsOfStart(address=self.debot_address)
        debot_browser(
            steps=steps, params=params, start_fn='start', keypair=self.keypair)

    def test_run_action(self):
        steps = [
            {'choice': 2, 'inputs': [], 'outputs': ['Test Run Action']},
            {'choice': 0, 'inputs': ['-1:1111111111111111111111111111111111111111111111111111111111111111'], 'outputs': ['Test Instant Run', 'test1: instant run 1', 'test2: instant run 2']},
            {'choice': 0, 'inputs': [], 'outputs': ['Test Run Action']},
            {'choice': 1, 'inputs': ['hello'], 'outputs': []},
            {'choice': 2, 'inputs': [], 'outputs': ['integer=2,addr=-1:1111111111111111111111111111111111111111111111111111111111111111,string=hello']},
            {'choice': 3, 'inputs': [], 'outputs': ['Debot Tests']},
            {'choice': 7, 'inputs': [], 'outputs': []}
        ]
        params = ParamsOfStart(address=self.debot_address)
        debot_browser(
            steps=steps, params=params, start_fn='start', keypair=self.keypair)

    def test_run_method(self):
        keypair = async_custom_client.crypto.generate_random_sign_keys()
        debot_address, _ = self.__deploy(keypair=keypair)

        steps = [
            {'choice': 3, 'inputs': [], 'outputs': ['Test Run Method Action']},
            {'choice': 0, 'inputs': [], 'outputs': []},
            {'choice': 1, 'inputs': [], 'outputs': ['data=64']},
            {'choice': 2, 'inputs': [], 'outputs': ['Debot Tests']},
            {'choice': 7, 'inputs': [], 'outputs': []}
        ]
        params = ParamsOfStart(address=debot_address)
        debot_browser(
            steps=steps, params=params, start_fn='start', keypair=keypair)

    def test_send_message(self):
        steps = [
            {'choice': 4, 'inputs': [], 'outputs': ['Test Send Msg Action']},
            {'choice': 0, 'inputs': [], 'outputs': ['Sending message {}', 'Transaction succeeded.']},
            {'choice': 1, 'inputs': [], 'outputs': []},
            {'choice': 2, 'inputs': [], 'outputs': ['data=100']},
            {'choice': 3, 'inputs': [], 'outputs': ['Debot Tests']},
            {'choice': 7, 'inputs': [], 'outputs': []}
        ]
        params = ParamsOfStart(address=self.debot_address)
        debot_browser(
            steps=steps, params=params, start_fn='start', keypair=self.keypair)

    def test_invoke(self):
        steps = [
            {'choice': 5, 'inputs': [self.debot_address], 'outputs': ['Test Invoke Debot Action', 'enter debot address:']},
            {'choice': 0, 'inputs': [self.debot_address], 'outputs': ['Test Invoke Debot Action', 'enter debot address:'], 'invokes': [
                {'choice': 0, 'inputs': [], 'outputs': ['Print test string', 'Debot is invoked']},
                {'choice': 0, 'inputs': [], 'outputs': ['Sending message {}', 'Transaction succeeded.']}
            ]},
            {'choice': 1, 'inputs': [], 'outputs': ['Debot Tests']},
            {'choice': 7, 'inputs': [], 'outputs': []}
        ]
        params = ParamsOfStart(address=self.debot_address)
        debot_browser(
            steps=steps, params=params, start_fn='start', keypair=self.keypair)

    def test_engine_calls(self):
        steps = [
            {'choice': 6, 'inputs': [], 'outputs': ['Test Engine Calls']},
            {'choice': 0, 'inputs': [], 'outputs': []},
            {'choice': 1, 'inputs': [], 'outputs': []},
            # {'choice': 2, 'inputs': [], 'outputs': []},
            {'choice': 3, 'inputs': [], 'outputs': []},
            {'choice': 4, 'inputs': [], 'outputs': []},
            {'choice': 5, 'inputs': [], 'outputs': ['Debot Tests']},
            {'choice': 7, 'inputs': [], 'outputs': []}
        ]
        params = ParamsOfStart(address=self.debot_address)
        debot_browser(
            steps=steps, params=params, start_fn='start', keypair=self.keypair)

    @staticmethod
    def debot_print_state(state: Dict[str, Any]):
        # Print messages
        for message in state['messages']:
            logging.info(f'[LOG]\t{message}')
        # Print available actions
        for action in state['actions']:
            logging.info(f'[ACTION]\t{action}')

    def __deploy(self, keypair: KeyPair) -> Tuple[str, str]:
        """ Deploy debot and target """
        signer = Signer.Keys(keys=keypair)

        # Deploy target
        call_set = CallSet(function_name='constructor')
        deploy_set = DeploySet(tvc=self.target_tvc)
        encode_params = ParamsOfEncodeMessage(
            abi=self.target_abi, signer=signer, deploy_set=deploy_set,
            call_set=call_set)
        message = async_custom_client.abi.encode_message(params=encode_params)

        # Check if target contract does not exists
        q_params = ParamsOfQueryCollection(
            collection='accounts', result='id',
            filter={'id': {'eq': message.address}})
        result = async_custom_client.net.query_collection(params=q_params)
        if len(result.result):
            target_address = result.result[0]['id']
        else:
            send_grams(address=message.address)
            process_params = ParamsOfProcessMessage(
                message_encode_params=encode_params, send_events=False)
            target = async_custom_client.processing.process_message(
                params=process_params)
            target_address = target.transaction['account_addr']

        # Deploy debot
        call_set = CallSet(
            function_name='constructor', input={
                'debotAbi': self.debot_abi.value.encode().hex(),
                'targetAbi': self.target_abi.value.encode().hex(),
                'targetAddr': target_address
            })
        deploy_set = DeploySet(tvc=self.debot_tvc)
        encode_params = ParamsOfEncodeMessage(
            abi=self.debot_abi, signer=signer, deploy_set=deploy_set,
            call_set=call_set)
        message = async_custom_client.abi.encode_message(params=encode_params)

        # Check if debot contract does not exists
        q_params = ParamsOfQueryCollection(
            collection='accounts', result='id',
            filter={'id': {'eq': message.address}})
        result = async_custom_client.net.query_collection(params=q_params)
        if len(result.result):
            debot_address = result.result[0]['id']
        else:
            send_grams(address=message.address)
            process_params = ParamsOfProcessMessage(
                message_encode_params=encode_params, send_events=False)
            debot = async_custom_client.processing.process_message(
                params=process_params)
            debot_address = debot.transaction['account_addr']

        return debot_address, target_address


def debot_browser(
        steps: List[Dict[str, Any]], start_fn: str, keypair: KeyPair,
        params: Union[ParamsOfStart, ParamsOfFetch],
        actions: List[DebotAction] = None):

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

    # Create initial state
    state: Dict[str, Any] = {
        'messages': [],
        'actions': actions or [],
        'steps': steps,
        'step': None,
        'switch_started': False,
        'finished': False
    }

    # Start debot browser and get handle
    debot = getattr(async_custom_client.debot, start_fn)(
        params=params, callback=__callback)
    TestTonDebotAsyncCore.debot_print_state(state=state)

    while not state['finished']:
        step: Dict[str, Any] = state['steps'].pop(0)
        action = state['actions'][step['choice']]
        logging.info(f'[ACTION SELECTED]\t{action}')
        state['messages'].clear()
        state['step'] = step

        exec_params = ParamsOfExecute(
            debot_handle=debot.debot_handle, action=action)
        async_custom_client.debot.execute(params=exec_params)
        TestTonDebotAsyncCore.debot_print_state(state=state)

        test_case = unittest.TestCase()
        test_case.assertEqual(
            len(state['step']['outputs']), len(state['messages']))

        if not len(state['steps']):
            break

    async_custom_client.debot.remove(params=debot)
