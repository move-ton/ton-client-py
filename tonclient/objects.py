import asyncio
import inspect
import re
from asyncio.selector_events import BaseSelectorEventLoop
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from multiprocessing import get_context
from typing import Dict, Any, Union, Coroutine

from tonclient.bindings.types import TCResponseType
from tonclient.client import TonClient
from tonclient.errors import TonException
from tonclient.types import ParamsOfAppRequest, AppRequestResult, \
    ParamsOfResolveAppRequest, AppRequestResultType, ResultOfAppSigningBox, \
    ParamsOfAppSigningBox, ResultOfAppEncryptionBox, EncryptionBoxInfo, \
    ParamsOfAppEncryptionBox, ParamsOfAppDebotBrowser, \
    ResultOfAppDebotBrowser, ParamsOfAppEncryptionBoxType, \
    ParamsOfAppSigningBoxType, ParamsOfAppDebotBrowserType


class AppObject(object):
    """ Base app object class """

    c2s_pattern = re.compile(r'(?<!^)(?=[A-Z])')

    def __init__(self, client: TonClient):
        if not client.is_core_async:
            raise Exception('Only `async core` client is supported')

        super(AppObject, self).__init__()
        self.client = client
        self._loop = None

    def dispatcher(
            self, response_data: Dict[str, Any], response_type: int,
            loop: Union[BaseSelectorEventLoop, None]):
        """
        Dispatcher method which should be passed to methods with app object
        callback argument

        :param response_data:
        :param response_type:
        :param loop:
        :return:
        """
        self._loop = loop

        if response_type == TCResponseType.AppRequest:
            params = ParamsOfAppRequest(**response_data)
            self.dispatch(
                params=params.request_data,
                app_request_id=params.app_request_id)

        if response_type == TCResponseType.AppNotify:
            self.dispatch(params=response_data)

    def dispatch(self, params: Dict[str, Any], app_request_id: int = None):
        """
        Dispatch object corresponding method and resolve app request if needed

        :param params: ParamsOfAppFoo
        :param app_request_id: App request id
        :return:
        """
        params = self._prepare_params(params=params)
        method = self.camel_to_snake(string=getattr(params, 'type'))
        try:
            with ThreadPoolExecutor() as executor:
                future = executor.submit(getattr(self, method), params)
                exception = future.exception()
                if exception:
                    raise exception.__class__(exception)
                result = future.result()

            if app_request_id:
                result = AppRequestResult.Ok(result=result.dict)
                self._resolve_app_request(
                    result=result, app_request_id=app_request_id)
        except TonException as e:
            if not app_request_id:
                raise

            result = AppRequestResult.Error(text=e.__str__())
            self._resolve_app_request(
                result=result, app_request_id=app_request_id)
        except Exception:
            raise

    def camel_to_snake(self, string: str) -> str:
        return self.c2s_pattern.sub('_', string).lower()

    def _prepare_params(self, params: Dict[str, Any]) -> object:
        raise NotImplementedError(
            f'{self.__class__.__name__} `_prepare_params` not implemented')

    def _resolve_app_request(
            self, result: AppRequestResultType, app_request_id: int):
        """
        :param result:
        :param app_request_id:
        :return:
        """
        resolve_params = ParamsOfResolveAppRequest(
            app_request_id=app_request_id, result=result)

        if self._loop:
            self._resolve_sync_async(
                method=self.client.resolve_app_request, params=resolve_params)
        else:
            with ThreadPoolExecutor() as executor:
                future = executor.submit(
                    self.client.resolve_app_request, params=resolve_params)
                future.result()

    def _resolve_sync_async(self, method: Any, *args, **kwargs) -> Any:
        result = method(*args, **kwargs)

        if inspect.isawaitable(result):
            future = asyncio.run_coroutine_threadsafe(
                coro=result, loop=self._loop)
            result = future.result()

        return result


class AppSigningBox(AppObject):
    """ AppSigningBox object """

    def get_public_key(self, _) -> ResultOfAppSigningBox.GetPublicKey:
        """ Method is called by `dispatch` """
        public_key = self._resolve_sync_async(
            method=self.perform_get_public_key)
        return ResultOfAppSigningBox.GetPublicKey(public_key=public_key)

    def perform_get_public_key(self) -> Union[str, Coroutine]:
        """
        :return: Box public key
        """
        raise NotImplementedError(
            'AppSigningBox `perform_get_public_key` must be implemented')

    def sign(
            self, params: ParamsOfAppSigningBox.Sign
    ) -> ResultOfAppSigningBox.Sign:
        """ Method is called by `dispatch` """
        signature = self._resolve_sync_async(
            method=self.perform_sign, params=params)
        return ResultOfAppSigningBox.Sign(signature=signature)

    def perform_sign(
            self, params: ParamsOfAppSigningBox.Sign) -> Union[str, Coroutine]:
        """
        :param params:
        :return: Signature
        """
        raise NotImplementedError(
            'AppSigningBox `perform_sign` must be implemented')

    def _prepare_params(
            self, params: Dict[str, Any]) -> ParamsOfAppSigningBoxType:
        return ParamsOfAppSigningBox.from_dict(data=params)


class AppEncryptionBox(AppObject):
    """ AppEncryptionBox object """

    def get_info(self, _) -> ResultOfAppEncryptionBox.GetInfo:
        """ Method is called by `dispatch` """
        info = self._resolve_sync_async(method=self.perform_get_info)
        return ResultOfAppEncryptionBox.GetInfo(info=info)

    def perform_get_info(self) -> Union[EncryptionBoxInfo, Coroutine]:
        raise NotImplementedError(
            'AppEncryptionBox `perform_get_info` must be implemented')

    def encrypt(
            self, params: ParamsOfAppEncryptionBox.Encrypt
    ) -> ResultOfAppEncryptionBox.Encrypt:
        """ Method is called by `dispatch` """
        data = self._resolve_sync_async(
            method=self.perform_encrypt, params=params)
        return ResultOfAppEncryptionBox.Encrypt(data=data)

    def perform_encrypt(
            self, params: ParamsOfAppEncryptionBox.Encrypt
    ) -> Union[str, Coroutine]:
        """
        :param params:
        :return: Encrypted data
        """
        raise NotImplementedError(
            'AppEncryptionBox `perform_encrypt` must be implemented')

    def decrypt(
            self, params: ParamsOfAppEncryptionBox.Decrypt
    ) -> ResultOfAppEncryptionBox.Decrypt:
        """ Method is called by `dispatch` """
        data = self._resolve_sync_async(
            method=self.perform_decrypt, params=params)
        return ResultOfAppEncryptionBox.Decrypt(data=data)

    def perform_decrypt(
            self, params: ParamsOfAppEncryptionBox.Decrypt
    ) -> Union[str, Coroutine]:
        """
        :param params:
        :return: Decrypted data
        """
        raise NotImplementedError(
            'AppEncryptionBox `perform_decrypt` must be implemented')

    def _prepare_params(
            self, params: Dict[str, Any]) -> ParamsOfAppEncryptionBoxType:
        return ParamsOfAppEncryptionBox.from_dict(data=params)


class AppDebotBrowser(AppObject):
    """ AppDebotBrowser object """

    def log(self, params: ParamsOfAppDebotBrowser.Log):
        """ Method is called by `dispatch` """
        self._resolve_sync_async(method=self.perform_log, params=params)

    def perform_log(self, params: ParamsOfAppDebotBrowser.Log):
        raise NotImplementedError(
            'AppDebotBrowser `perform_log` must be implemented')

    def switch(self, params: ParamsOfAppDebotBrowser.Switch):
        """ Method is called by `dispatch` """
        self._resolve_sync_async(method=self.perform_switch, params=params)

    def perform_switch(self, params: ParamsOfAppDebotBrowser.Switch):
        raise NotImplementedError(
            'AppDebotBrowser `perform_switch` must be implemented')

    def switch_completed(self, _):
        """ Method is called by `dispatch` """
        self._resolve_sync_async(method=self.perform_switch_completed)

    def perform_switch_completed(self):
        raise NotImplementedError(
            'AppDebotBrowser `perform_switch_completed` must be implemented')

    def show_action(self, params: ParamsOfAppDebotBrowser.ShowAction):
        self._resolve_sync_async(
            method=self.perform_show_action, params=params)

    def perform_show_action(self, params: ParamsOfAppDebotBrowser.ShowAction):
        raise NotImplementedError(
            'AppDebotBrowser `perform_show_action` must be implemented')

    def input(
            self, params: ParamsOfAppDebotBrowser.Input
    ) -> ResultOfAppDebotBrowser.Input:
        """ Method is called by `dispatch` """
        value = self._resolve_sync_async(
            method=self.perform_input, params=params)

        return ResultOfAppDebotBrowser.Input(value=value)

    def perform_input(
            self, params: ParamsOfAppDebotBrowser.Input
    ) -> Union[str, Coroutine]:
        """
        :param params:
        :return: Value that would be inputted to DeBot
        """
        raise NotImplementedError(
            'AppDebotBrowser `perform_input` must be implemented')

    def get_signing_box(self, _) -> ResultOfAppDebotBrowser.GetSigningBox:
        """ Method is called by `dispatch` """
        signing_box = self._resolve_sync_async(
            method=self.perform_get_signing_box)

        return ResultOfAppDebotBrowser.GetSigningBox(signing_box=signing_box)

    def perform_get_signing_box(self) -> Union[int, Coroutine]:
        """
        :return: Signing box handle
        """
        raise NotImplementedError(
            'AppDebotBrowser `perform_get_signing_box` must be implemented')

    def invoke_debot(
            self, params: ParamsOfAppDebotBrowser.InvokeDebot
    ) -> ResultOfAppDebotBrowser.InvokeDebot:
        """ Method is called by `dispatch` """
        # We should call `perform_invoke_debot` in `spawn` mode subprocess
        # for compatibility with `Unix` systems.
        # MacOS, Windows use `spawn` by default
        with ProcessPoolExecutor(mp_context=get_context('spawn')) as pool:
            future = pool.submit(
                self.perform_invoke_debot, client=self.client, params=params)
            future.result()

        return ResultOfAppDebotBrowser.InvokeDebot()

    @staticmethod
    def perform_invoke_debot(
            client: TonClient, params: ParamsOfAppDebotBrowser.InvokeDebot,
            *args, **kwargs):
        raise NotImplementedError(
            'AppDebotBrowser `perform_invoke_debot` must be implemented')

    def send(self, params: ParamsOfAppDebotBrowser.Send):
        """ Method is called by `dispatch` """
        self._resolve_sync_async(method=self.perform_send, params=params)

    def perform_send(self, params: ParamsOfAppDebotBrowser.Send):
        raise NotImplementedError(
            'AppDebotBrowser `perform_send` must be implemented')

    def approve(
            self, params: ParamsOfAppDebotBrowser.Approve
    ) -> ResultOfAppDebotBrowser.Approve:
        """ Method is called by `dispatch` """
        approved = self._resolve_sync_async(
            method=self.perform_approve, params=params)

        return ResultOfAppDebotBrowser.Approve(approved=approved)

    def perform_approve(
            self, params: ParamsOfAppDebotBrowser.Approve
    ) -> Union[bool, Coroutine]:
        """
        :param params:
        :return: DeBot is/is not allowed to perform the specified operation
        """
        raise NotImplementedError(
            'AppDebotBrowser `perform_approve` must be implemented')

    def _prepare_params(
            self, params: Dict[str, Any]) -> ParamsOfAppDebotBrowserType:
        return ParamsOfAppDebotBrowser.from_dict(data=params)
