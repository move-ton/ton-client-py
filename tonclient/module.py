import asyncio
import logging
import os

import json
import time
from typing import Any, Dict, Union, Generator, Tuple, List

from tonclient.bindings.lib import tc_request, tc_request_sync, \
    tc_read_string, tc_destroy_string
from tonclient.bindings.types import TCStringData, TCResponseHandler, \
    TCResponseType, TCSyncResponseData
from tonclient.errors import TonException


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
            self, method: str, as_iterable: bool = False,
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
            kwargs.update({'as_iterable': as_iterable})
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
            raise TonException(error=error)

        return result

    def _async_core_request(
            self, method: str, request_params: str, as_iterable: bool
    ) -> Union[Generator, Any]:
        """ Perform core asynchronous request """
        # Perform async core request
        request_id = self._generate_request_id()
        self._async_response_map[request_id] = []
        tc_request(
            ctx=self._client.ctx, method=method, request_id=request_id,
            params_json=request_params,
            response_handler=self._async_response_handler)

        if as_iterable:
            if self._client.is_async:
                return self._async_response_generator_coro(
                    request_id=request_id)
            return self._async_response_generator(request_id=request_id)

        if self._client.is_async:
            return self._async_response_resolver_coro(request_id=request_id)
        return self._async_response_resolver(request_id=request_id)

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

    def _async_response_resolver(self, request_id: int) -> Any:
        read_len = 0
        result = None
        while True:
            time.sleep(0.001)
            read_len, finished, tmp_result = self._async_response_resolve(
                request_id=request_id, read_len=read_len)
            if tmp_result is not None:
                result = tmp_result
            if finished:
                return result

    async def _async_response_resolver_coro(self, request_id: int) -> Any:
        read_len = 0
        result = None
        while True:
            await asyncio.sleep(0.001)
            read_len, finished, tmp_result = self._async_response_resolve(
                request_id=request_id, read_len=read_len)
            if tmp_result is not None:
                result = tmp_result
            if finished:
                return result

    def _async_response_generator(self, request_id: int) -> Any:
        read_len = 0
        while True:
            time.sleep(0.001)
            read_len, package = self._async_response_generator_resolve(
                    request_id=request_id, read_len=read_len)
            for item in package:
                if item['finished']:
                    yield item
                    return
                yield item

    async def _async_response_generator_coro(self, request_id: int) -> Any:
        read_len = 0
        while True:
            await asyncio.sleep(0.001)
            read_len, package = self._async_response_generator_resolve(
                request_id=request_id, read_len=read_len)
            for item in package:
                if item['finished']:
                    yield item
                    return
                yield item

    def _async_response_resolve(
            self, request_id: int, read_len: int) -> Tuple[int, bool, Any]:
        """
        Resolve responses from async core request
        :param request_id: Request id
        :param read_len: Responses len, that have been already read
        :return:
        """
        responses = self._async_response_map[request_id][read_len:]
        read_len += len(responses)
        result = None
        finished = False
        for item in responses:
            if item['response_type'] == TCResponseType.Error:
                del self._async_response_map[request_id]
                raise TonException(item['response_data'])
            if item['response_type'] == TCResponseType.Success:
                result = item['response_data']
            if item['finished']:
                del self._async_response_map[request_id]
                finished = True
        return read_len, finished, result

    def _async_response_generator_resolve(
            self, request_id: int, read_len: int) -> Tuple[int, List[Any]]:
        """
        Filter async core request responses and add extra logic
        :param request_id: Request id
        :param read_len: Responses len, that have been already read
        :return:
        """
        responses = self._async_response_map[request_id][read_len:]
        read_len += len(responses)
        filtered = []
        for item in responses:
            if item['response_type'] == TCResponseType.Error:
                del self._async_response_map[request_id]
                raise TonException(item['response_data'])
            if item['finished']:
                del self._async_response_map[request_id]
            filtered.append(item)
        return read_len, filtered

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
        response = {
            'response_data': response_data.json,
            'response_type': response_type,
            'finished': finished
        }
        logging.debug(f'Request: {request_id}; Response: {response}')
        if TonModule._async_response_map.get(request_id) is not None:
            TonModule._async_response_map[request_id].append(response)
