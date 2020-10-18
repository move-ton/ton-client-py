from typing import Any


class TonException(Exception):
    def __init__(self, error: Any):
        if type(error) is dict:
            error = f"[{error.get('code')}] {error.get('message')} " \
                    f"(Core: {error.get('data', {}).get('core_version')})"
        super(TonException, self).__init__(error)
