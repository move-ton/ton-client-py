import logging
import os

import json
import time
from json.decoder import JSONDecodeError
from typing import Any, Dict, Union

from tonclient.bindings.lib import tc_request, tc_request_sync, \
    tc_read_string, tc_destroy_string
from tonclient.bindings.types import TCStringData, TCResponseHandler, \
    TCResponseType, TCSyncResponseData
from tonclient.errors import TonException

logging.basicConfig(level=os.environ.get('LOGLEVEL', 'INFO').upper())
logger = logging.getLogger('TONClient')


class TonModule(object):
    """
    Base TON Module class.
    All modules, such as 'crypto', 'contracts', etc. should be inherited
    from this class.
    """
    _async_response_map = {}

    def __init__(self, client):
        self._client = client

    @staticmethod
    def _prepare_params(params_or_str, **kwargs) -> str:
        """ Prepare params to pass to request """
        if isinstance(params_or_str, dict):
            params_or_str = {**params_or_str, **kwargs}
        elif params_or_str is None:
            params_or_str = kwargs or {}

        return json.dumps(params_or_str)

    def request(
            self, method: str, is_generator: bool = False,
            params_or_str: Union[str, Dict[str, Any]] = None, **kwargs) -> Any:
        """ Perform core request """
        # Prepare request params
        request_params = self._prepare_params(params_or_str, **kwargs)
        kwargs = {
            'method': method,
            'request_params': request_params
        }

        # Make sync or async/asyncgen request
        if not self._client.is_async:
            return self._request_sync(**kwargs)
        if is_generator:
            return self._request_asyncgen(**kwargs)
        return self._request_async(**kwargs)

    def _request_sync(self, method: str, request_params: str) -> Any:
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

    def _request_async(self, method: str, request_params: str):
        """ Perform core asynchronous request and return result """
        # Perform async core request
        request_id = self._client.async_request_id
        tc_request(
            ctx=self._client.ctx, method=method, request_id=request_id,
            params_json=request_params,
            response_handler=self._async_response_handler)
        self._client.async_request_id += 1

        # Wait for result
        while True:
            time.sleep(0.0001)
            responses = self._async_response_map.get(request_id, [])
            if not responses:
                continue

            if responses[-1]['response_type'] == TCResponseType.Error:
                raise TonException(responses[-1]['response_data'])

            if responses[-1]['finished']:
                del self._async_response_map[request_id]
                return responses[-1]['response_data']

    def _request_asyncgen(self, method: str, request_params: str):
        """ Perform core asynchronous request and yield results """
        # Perform async core request
        request_id = self._client.async_request_id
        tc_request(
            ctx=self._client.ctx, method=method, request_id=request_id,
            params_json=request_params,
            response_handler=self._async_response_handler)
        self._client.async_request_id += 1

        # Yield received responses
        def __generator(_request_id):
            while True:
                time.sleep(0.0001)
                responses = self._async_response_map.get(request_id, [])
                if not responses:
                    continue

                if responses[-1]['response_type'] == TCResponseType.Error:
                    raise TonException(responses[-1]['response_data'])

                try:
                    for item in responses:
                        yield item['response_data']
                    if responses[-1]['finished']:
                        break
                    responses.clear()
                except GeneratorExit:
                    break

            del self._async_response_map[request_id]
            return

        return __generator(_request_id=request_id)

    @staticmethod
    @TCResponseHandler
    def _async_response_handler(
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

        if not TonModule._async_response_map.get(request_id):
            TonModule._async_response_map[request_id] = []
        TonModule._async_response_map[request_id].append(response)
