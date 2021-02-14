import asyncio
import logging
import os

import json
from concurrent.futures import Future
from typing import Any, Dict, Union

from tonclient.bindings.lib import tc_request, tc_request_sync, \
    tc_read_string, tc_destroy_string
from tonclient.bindings.types import TCStringData, TCResponseHandler, \
    TCResponseType, TCSyncResponseData
from tonclient.errors import TonException
from tonclient.types import ClientError, ResponseHandler


class TonModule(object):
    """
    Base TON Module class.
    All modules, such as 'crypto', 'contracts', etc. should be inherited
    from this class.
    """
    _async_response_map = {}

    def __init__(self, client):
        self._client = client

    def request(
            self, method: str, callback: ResponseHandler = None,
            params_or_str: Union[str, Dict[str, Any]] = None, **kwargs) -> Any:
        """ Perform core request """
        # Prepare request params
        request_params = self._prepare_params(params_or_str, **kwargs)
        kwargs = {
            'method': method,
            'request_params': request_params
        }

        # Make sync or async core/client request
        if self._client.is_core_async:
            kwargs.update({'callback': callback})
            if self._client.is_async:
                return self._async_core_request_future(**kwargs)
            return self._async_core_request(**kwargs)
        return self._sync_core_request(**kwargs)

    def _sync_core_request(self, method: str, request_params: str) -> Any:
        """ Perform core synchronous request """
        # Make sync request, get response pointer and parse it
        response_ptr = tc_request_sync(
            ctx=self._client.ctx, method=method, params_json=request_params)
        response = TCSyncResponseData(tc_read_string(string=response_ptr))

        # Copy response data and destroy response pointer
        is_success, result, error = (
            response.is_success, response.result, response.error)
        tc_destroy_string(string=response_ptr)

        if not is_success:
            raise TonException(error=ClientError(**error))

        return result

    def _async_core_request(
            self, method: str, request_params: str, callback: ResponseHandler
    ) -> Any:
        """ Perform core asynchronous request """
        # Generate request id
        request_id = self._generate_request_id()

        # Create concurrent future
        future = Future()

        # Set response map data
        self._async_response_map[request_id] = {
            'is_async': False,
            'callback': callback,
            'future': future
        }

        # Execute core request
        tc_request(
            ctx=self._client.ctx, method=method, request_id=request_id,
            params_json=request_params,
            response_handler=self._async_response_handler)

        # Resolve future
        exception = future.exception()
        if exception:
            raise exception
        return future.result()

    async def _async_core_request_future(
            self, method: str, request_params: str, callback: ResponseHandler
    ) -> Any:
        """ Perform core asynchronous request """
        # Generate request id
        request_id = self._generate_request_id()

        # Get event loop and create future
        loop = asyncio.get_event_loop()
        future = loop.create_future()

        # Set response map data
        self._async_response_map[request_id] = {
            'is_async': True,
            'callback': callback,
            'loop': loop,
            'future': future
        }

        # Execute core request
        tc_request(
            ctx=self._client.ctx, method=method, request_id=request_id,
            params_json=request_params,
            response_handler=self._async_response_handler)

        return await future

    def _generate_request_id(self, size: int = 3) -> int:
        """
        Generate random int of size in bytes
        :param size: Length in bytes
        :return:
        """
        while True:
            request_id = int.from_bytes(os.urandom(size), 'big')
            if request_id in list(self._async_response_map.keys()):
                continue
            return request_id

    @staticmethod
    def _prepare_params(params_or_str, **kwargs) -> str:
        """ Prepare params to pass to request """
        if isinstance(params_or_str, dict):
            params_or_str = {**params_or_str, **kwargs}
        elif params_or_str is None:
            params_or_str = kwargs or {}

        return json.dumps(params_or_str)

    @staticmethod
    @TCResponseHandler
    def _async_response_handler(
            request_id: int, response_data: TCStringData,
            response_type: int, finished: bool):
        """ Core response handler """
        logging.debug(
            f'Request: {request_id}; Response: {response_data.json}; '
            f'Response type: {response_type}; Finished: {finished}')

        request = TonModule._async_response_map.get(request_id)
        if not request:
            return
        if finished:
            del TonModule._async_response_map[request_id]

        if response_type == TCResponseType.Success:
            # Check if client is asyncio or common
            if request['is_async']:
                request['loop'].call_soon_threadsafe(
                    request['future'].set_result, response_data.json)
            else:
                request['future'].set_result(response_data.json)
            return

        if response_type == TCResponseType.Error:
            exception = TonException(error=ClientError(**response_data.json))
            # Check if client is asyncio or common
            if request['is_async']:
                request['loop'].call_soon_threadsafe(
                    request['future'].set_exception, exception)
            else:
                request['future'].set_exception(exception)
            return

        if request['callback'] and response_data.json:
            args = [response_data.json, response_type, request.get('loop')]
            request['callback'](*args)
