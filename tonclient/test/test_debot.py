import asyncio
import base64
import os
import unittest
import logging
from typing import List, Dict, Tuple, Any

from tonclient.bindings.types import TCResponseType
from tonclient.client import TonClient
from tonclient.test.helpers import CUSTOM_BASE_URL, SAMPLES_DIR, \
    async_custom_client, send_grams
from tonclient.types import Abi, Signer, CallSet, DeploySet, DebotAction, \
    DebotState, AppRequestResult, ParamsOfAppDebotBrowser, \
    ResultOfAppDebotBrowser

client = TonClient(network={'server_address': CUSTOM_BASE_URL}, is_async=True)


class TestTonDebotAsyncCore(unittest.TestCase):
    def setUp(self) -> None:
        self.keypair = async_custom_client.crypto.generate_random_sign_keys()
        self.target_abi = Abi.from_path(
            path=os.path.join(SAMPLES_DIR, 'DebotTarget.abi.json'))
        self.debot_abi = Abi.from_path(
            path=os.path.join(SAMPLES_DIR, 'Debot.abi.json'))
        with open(os.path.join(SAMPLES_DIR, 'DebotTarget.tvc'), 'rb') as fp:
            self.target_tvc = base64.b64encode(fp.read()).decode()
        with open(os.path.join(SAMPLES_DIR, 'Debot.tvc'), 'rb') as fp:
            self.debot_tvc = base64.b64encode(fp.read()).decode()

        self.debot_address, self.target_address = self.__deploy()

    def test_goto(self):
        steps = [
            {'choice': 0, 'inputs': [], 'outputs': ['Test Goto Action'], 'actions': 1},
            {'choice': 0, 'inputs': [], 'outputs': ['Debot Tests'], 'actions': 8},
            {'choice': 7, 'inputs': [], 'outputs': [], 'actions': 0}
        ]
        asyncio.get_event_loop().run_until_complete(
            self._debot_run(steps=steps))

    def test_print(self):
        steps = [
            {'choice': 1, 'inputs': [], 'outputs': ['Test Print Action', 'test2: instant print', 'test instant print'], 'actions': 3},
            {'choice': 0, 'inputs': [], 'outputs': ['test simple print'], 'actions': 3},
            {'choice': 1, 'inputs': [], 'outputs': [f'integer=1,addr={self.target_address},string=test_string_1'], 'actions': 3},
            {'choice': 2, 'inputs': [], 'outputs': ['Debot Tests'], 'actions': 8},
            {'choice': 7, 'inputs': [], 'outputs': [], 'actions': 0}
        ]
        asyncio.get_event_loop().run_until_complete(
            self._debot_run(steps=steps))

    def test_run(self):
        steps = [
            {'choice': 2, 'inputs': '-1:1111111111111111111111111111111111111111111111111111111111111111', 'outputs': ['Test Run Action', 'test1: instant run 1', 'test2: instant run 2'], 'actions': 3},
            {'choice': 0, 'inputs': 'hello', 'outputs': [], 'actions': 3},
            {'choice': 1, 'inputs': [], 'outputs': ['integer=2,addr=-1:1111111111111111111111111111111111111111111111111111111111111111,string=hello'], 'actions': 3},
            {'choice': 2, 'inputs': [], 'outputs': ['Debot Tests'], 'actions': 8},
            {'choice': 7, 'inputs': [], 'outputs': [], 'actions': 0}
        ]
        asyncio.get_event_loop().run_until_complete(
            self._debot_run(steps=steps))

    def test_run_method(self):
        steps = [
            {'choice': 3, 'inputs': [], 'outputs': ['Test Run Method Action'], 'actions': 3},
            {'choice': 0, 'inputs': [], 'outputs': [], 'actions': 3},
            {'choice': 1, 'inputs': [], 'outputs': ['data=64'], 'actions': 3},
            {'choice': 2, 'inputs': [], 'outputs': ['Debot Tests'], 'actions': 8},
            {'choice': 7, 'inputs': [], 'outputs': [], 'actions': 0}
        ]
        asyncio.get_event_loop().run_until_complete(
            self._debot_run(steps=steps))

    def test_send_message(self):
        steps = [
            {'choice': 4, 'inputs': [], 'outputs': ['Test Send Msg Action'], 'actions': 4},
            {'choice': 0, 'inputs': [], 'outputs': ['Sending message {}', 'Transaction succeeded.'], 'actions': 4},
            {'choice': 1, 'inputs': [], 'outputs': [], 'actions': 4},
            {'choice': 2, 'inputs': [], 'outputs': ['data=100'], 'actions': 4},
            {'choice': 3, 'inputs': [], 'outputs': ['Debot Tests'], 'actions': 8},
            {'choice': 7, 'inputs': [], 'outputs': [], 'actions': 0}
        ]
        asyncio.get_event_loop().run_until_complete(
            self._debot_run(steps=steps))

    def test_invoke(self):
        steps = [
            {'choice': 5, 'inputs': self.debot_address, 'outputs': ['Test Invoke Debot Action', 'enter debot address:'], 'actions': 2},
            {'choice': 0, 'inputs': [], 'outputs': [], 'actions': 2, 'invokes': [
                {'choice': 0, 'inputs': [], 'outputs': ['Print test string', 'Debot is invoked'], 'actions': 0}
            ]},
            {'choice': 1, 'inputs': [], 'outputs': ['Debot Tests'], 'actions': 8},
            {'choice': 7, 'inputs': [], 'outputs': [], 'actions': 0}
        ]
        asyncio.get_event_loop().run_until_complete(
            self._debot_run(steps=steps))

    async def _debot_run(
            self, steps: List[Dict[str, Any]], start_fn: str = 'start',
            actions: List[DebotAction] = None):
        # Create initial state
        state = {
            'handle': None,
            'messages': [],
            'actions': actions or [],
            'steps': steps,
            'step': None
        }

        # Start debot browser and wait for handle
        asyncio.get_running_loop().create_task(
            self._debot_browser(state=state, start_fn=start_fn))
        await self._debot_handle_await(state=state)
        self._debot_print_state(state=state)

        while len(state['steps']):
            step = state['steps'].pop(0)
            action = state['actions'][step['choice']]
            logging.info(f'[ACTION SELECTED]\t{action}')
            state['messages'].clear()
            state['step'] = step
            await client.debot.execute(
                debot_handle=state['handle'], action=action)
            while len(state['messages']) != len(step['outputs']) or \
                    len(state['actions']) != step['actions']:
                await asyncio.sleep(1)
            self._debot_print_state(state=state)
        await client.debot.remove(debot_handle=state['handle'])

    async def _debot_browser(self, state: Dict[str, Any], start_fn: str):
        generator = getattr(client.debot, start_fn)(address=self.debot_address)
        async for event in generator:
            data = event['response_data']
            # Check for useful data to be present
            if data is None:
                continue

            # Set state handle when received
            if event['response_type'] == TCResponseType.Success:
                state['handle'] = data['debot_handle']

            # Process app notifications
            if event['response_type'] == TCResponseType.AppNotify:
                params = ParamsOfAppDebotBrowser.from_dict(data=data)
                if isinstance(params, ParamsOfAppDebotBrowser.Log):
                    state['messages'].append(params.msg)
                if isinstance(params, ParamsOfAppDebotBrowser.Switch):
                    state['actions'].clear()
                    if params.context_id == DebotState.EXIT:
                        break
                if isinstance(params, ParamsOfAppDebotBrowser.ShowAction):
                    state['actions'].append(params.action)

            # Process app requests
            if event['response_type'] == TCResponseType.AppRequest:
                params = ParamsOfAppDebotBrowser.from_dict(
                    data=data['request_data'])
                result = None

                if isinstance(params, ParamsOfAppDebotBrowser.Input):
                    result = ResultOfAppDebotBrowser.Input(
                        value=state['step']['inputs'])
                if isinstance(params, ParamsOfAppDebotBrowser.GetSigningBox):
                    box = await client.crypto.get_signing_box(
                        keypair=self.keypair)
                    result = ResultOfAppDebotBrowser.GetSigningBox(
                        signing_box=box)
                if isinstance(params, ParamsOfAppDebotBrowser.InvokeDebot):
                    await self._debot_run(
                        steps=state['step']['invokes'], start_fn='fetch',
                        actions=[params.action])
                    result = ResultOfAppDebotBrowser.InvokeDebot()

                # Resolve app request
                result = AppRequestResult.Ok(result=result.dict)
                await client.resolve_app_request(
                    app_request_id=data['app_request_id'], result=result)

    @staticmethod
    async def _debot_handle_await(state: Dict[str, Any]):
        while True:
            await asyncio.sleep(0.1)
            if state['handle']:
                break

    @staticmethod
    def _debot_print_state(state: Dict[str, Any]):
        # Print messages
        for log in state['messages']:
            logging.info(f'[LOG]\t{log}')
        # Print available actions
        for action in state['actions']:
            logging.info(f'[ACTION]\t{action}')

    def __deploy(self) -> Tuple[str, str]:
        """ Deploy debot and target """
        signer = Signer.from_keypair(keypair=self.keypair)

        # Deploy target
        call_set = CallSet(function_name='constructor')
        deploy_set = DeploySet(tvc=self.target_tvc)
        deploy_kwargs = {
            'abi': self.target_abi,
            'signer': signer,
            'deploy_set': deploy_set,
            'call_set': call_set
        }
        message = async_custom_client.abi.encode_message(**deploy_kwargs)
        send_grams(address=message['address'])
        target = async_custom_client.processing.process_message(
            send_events=False, **deploy_kwargs)

        # Deploy debot
        call_set = CallSet(
            function_name='constructor', inputs={
                'debotAbi': self.debot_abi.abi.encode().hex(),
                'targetAbi': self.target_abi.abi.encode().hex(),
                'targetAddr': target['transaction']['account_addr']
            })
        deploy_set = DeploySet(tvc=self.debot_tvc)
        deploy_kwargs = {
            'abi': self.debot_abi,
            'signer': signer,
            'deploy_set': deploy_set,
            'call_set': call_set
        }
        message = async_custom_client.abi.encode_message(**deploy_kwargs)
        send_grams(address=message['address'])
        debot = async_custom_client.processing.process_message(
            send_events=False, **deploy_kwargs)

        return (
            debot['transaction']['account_addr'],
            target['transaction']['account_addr']
        )
