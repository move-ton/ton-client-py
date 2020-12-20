from typing import Any

from tonclient.types import ClientError


class TonException(Exception):
    def __init__(self, error: Any):
        if isinstance(error, ClientError):
            error = error.__str__()
        super(TonException, self).__init__(error)
