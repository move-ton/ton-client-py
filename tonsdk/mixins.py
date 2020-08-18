import json
from typing import Any

from tonsdk.bindings.lib import tc_json_request, tc_read_json_response, \
    tc_destroy_json_response
from tonsdk.errors import TonException


class TonRequestMixin:
    _ctx = None

    def request(self, method: str, arg: Any = None, **kwargs) -> Any:
        """ Fire TON lib request. Raise on error. """
        # Make request, get response pointer and read it
        params_json = arg if arg else kwargs or {}
        response_ptr = tc_json_request(
            ctx=self._ctx, method=method, params_json=json.dumps(params_json))
        response = tc_read_json_response(handle=response_ptr)

        # Copy response data and destroy response pointer
        is_success, result_json = (response.is_success, response.json)
        tc_destroy_json_response(response_ptr)

        # Process response
        if not is_success:
            raise TonException(result_json)

        return result_json
