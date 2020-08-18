import asyncio
import ctypes
import logging

import json
from typing import Any, Dict, Union

from tonsdk.bindings.lib import tc_json_request, tc_read_json_response, \
    tc_destroy_json_response, tc_json_request_async
from tonsdk.bindings.types import TCOnResponseT, TCResponseT, TCStringT
from tonsdk.errors import TonException

logger = logging.getLogger("ton")


class TonRequestMixin:
    def __init__(self):
        """ Dummy method for class logic flow """
        self._ctx = None
        self._async_request_id = 1

    @staticmethod
    def _prepare_params(arg, **kwargs):
        """ Prepare params to pass to request """
        return json.dumps(arg if arg else kwargs or {})

    def request(self, method: str, arg: Any = None, **kwargs) -> Any:
        """ Fire TON lib request. Raise on error. """
        # Make request, get response pointer and read it
        params_json = self._prepare_params(arg, **kwargs)
        response_ptr = tc_json_request(
            ctx=self._ctx, method=method, params_json=params_json)
        response = tc_read_json_response(handle=response_ptr)

        # Copy response data and destroy response pointer
        is_success, result_json = (response.is_success, response.json)
        tc_destroy_json_response(response_ptr)

        # Process response
        if not is_success:
            raise TonException(result_json)

        return result_json

    async def request_async(self, method: str, arg: Any = None, **kwargs):
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

        params_json = self._prepare_params(arg, **kwargs)
        tc_json_request_async(
            ctx=self._ctx, method=method, request_id=self._async_request_id,
            callback=_cb, params_json=params_json)

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
