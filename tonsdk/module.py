import asyncio
import ctypes

import json
from typing import Any, Dict, Union

from tonsdk.bindings.lib import tc_json_request, tc_read_json_response, \
    tc_destroy_json_response, tc_json_request_async
from tonsdk.bindings.types import TCOnResponseT, TCResponseT, TCStringT
from tonsdk.errors import TonException


class TonRequestMixin:
    def __init__(self):
        """ Dummy method for class logic flow """
        self._ctx = None
        self._async_request_id = 1

    @staticmethod
    def _prepare_params(params_or_str, **kwargs):
        """ Prepare params to pass to request """
        if isinstance(params_or_str, dict):
            params_or_str = {**params_or_str, **kwargs}
        elif params_or_str is None:
            params_or_str = kwargs or {}

        return json.dumps(params_or_str)

    def request(
            self, method: str,
            params_or_str: Union[str, Dict[str, Any]] = None, **kwargs) -> Any:
        """ Fire TON lib request. Raise on error. """
        # Make request, get response pointer and read it
        request_params = self._prepare_params(params_or_str, **kwargs)
        response_ptr = tc_json_request(
            ctx=self._ctx, method=method, params_json=request_params)
        response = tc_read_json_response(handle=response_ptr)

        # Copy response data and destroy response pointer
        is_success, result_json = (response.is_success, response.json)
        tc_destroy_json_response(response_ptr)

        # Process response
        if not is_success:
            raise TonException(result_json)

        return result_json

    async def request_async(
            self, method: str,
            params_or_str: Union[str, Dict[str, Any]] = None, **kwargs):
        loop = asyncio.get_running_loop()
        future = loop.create_future()

        @TCOnResponseT
        def _cb(
                request_id: int, result_json: TCStringT, error_json: TCStringT,
                flags: int):
            response = TCResponseT()
            response.result_json = result_json
            response.error_json = error_json

            future.set_result({
                'request_id': request_id,
                'result': response.json,
                'flags': flags
            })

        request_params = self._prepare_params(params_or_str, **kwargs)
        tc_json_request_async(
            ctx=self._ctx, method=method, request_id=self._async_request_id,
            callback=_cb, params_json=request_params)

        self._async_request_id += 1
        return await future


class TonModule(TonRequestMixin):
    """
    Base TON Module class.
    All modules, such as 'crypto', 'contracts', etc. should be inherited
    from this class.
    """
    def __init__(self, ctx: ctypes.c_int32):
        super(TonModule, self).__init__()
        self._ctx = ctx
