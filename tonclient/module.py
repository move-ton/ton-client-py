import asyncio
import ctypes
import logging
import os

import json
from json.decoder import JSONDecodeError
from typing import Any, Dict, Union, Awaitable

from tonclient.bindings.lib import tc_request, tc_request_sync, \
    tc_read_string, tc_destroy_string
from tonclient.bindings.types import TCStringData, TCResponseHandler, \
    TCResponseType, TCSyncResponseData
from tonclient.errors import TonException

logging.basicConfig(level=os.environ.get('LOGLEVEL', 'DEBUG').upper())
logger = logging.getLogger('TONClient')


class TonModule(object):
    """
    Base TON Module class.
    All modules, such as 'crypto', 'contracts', etc. should be inherited
    from this class.
    """
    def __init__(self, ctx: ctypes.c_int32, is_async: bool = False):
        self._ctx = ctx
        self._async_request_id = 1
        self.is_async = is_async

    @staticmethod
    def _prepare_params(params_or_str, **kwargs) -> str:
        """ Prepare params to pass to request """
        if isinstance(params_or_str, dict):
            params_or_str = {**params_or_str, **kwargs}
        elif params_or_str is None:
            params_or_str = kwargs or {}

        return json.dumps(params_or_str)

    def request(
            self, function_name: str,
            params_or_str: Union[str, Dict[str, Any]] = None, **kwargs) -> Any:
        """ Perform core request """
        # Prepare request params
        request_params = self._prepare_params(params_or_str, **kwargs)

        # Make sync or async request
        kwargs = {
            'function_name': function_name,
            'request_params': request_params
        }
        if self.is_async:
            return self._request(**kwargs)
        return self._request_sync(**kwargs)

    def _request_sync(self, function_name: str, request_params: str) -> Any:
        """ Perform core synchronous request """
        # Make sync request, get response pointer and parse it
        response_ptr = tc_request_sync(
            ctx=self._ctx, function_name=function_name,
            params_json=request_params)
        response = TCSyncResponseData(tc_read_string(string=response_ptr))

        # Copy response data and destroy response pointer
        is_success, result, error = (
            response.is_success, response.result, response.error)
        tc_destroy_string(string=response_ptr)

        if not is_success:
            raise TonException(error=error)

        return result

    async def _request(
            self, function_name: str, request_params: str) -> Awaitable:
        """ Perform core asynchronous request """
        async def _receive():
            """ Coro to wait for all core callbacks """
            while True:
                if not responses:
                    continue
                if responses[-1]['response_type'] == TCResponseType.Error:
                    raise TonException(error=responses[-1]['response_data'])
                if responses[-1]['finished']:
                    return responses[-1]['response_data']
                await asyncio.sleep(0.001)

        @TCResponseHandler
        def _response_handler(
                request_id: int, response_data: TCStringData,
                response_type: int, finished: bool):
            """ Core response handler """
            try:
                result = response_data.json
            except JSONDecodeError:
                result = response_data.string

            response = {
                'request_id': request_id,
                'response_data': result,
                'response_type': response_type,
                'finished': finished
            }
            logger.debug(response)
            responses.append(response)

        # Create awaitable task to receive all core callbacks and storage
        # for future responses.
        task = asyncio.get_running_loop().create_task(_receive())
        responses = []

        # Perform async core request
        tc_request(
            ctx=self._ctx, function_name=function_name,
            request_id=self._async_request_id,
            response_handler=_response_handler, params_json=request_params)

        self._async_request_id += 1
        return await task
