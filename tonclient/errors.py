"""Exception classes"""
from enum import EnumMeta
from typing import Any, Tuple, Union

from tonclient.types import (
    ClientError,
    AbiErrorCode,
    ClientErrorCode,
    BocErrorCode,
    CryptoErrorCode,
    NetErrorCode,
    ProcessingErrorCode,
    TvmErrorCode,
    DebotErrorCode,
    ProofsErrorCode,
)


class TonException(Exception):
    """TonException object"""

    client_error = None

    def __init__(self, error: Any):
        if isinstance(error, ClientError):
            self.client_error = error

            # Resolve module and error code verbose name
            module, err_name = self.get_module(code=error.code)
            error = '\n{:10s} {}\n{:10s} {} ({})\n{:10s} {}\n{:10s} {}'.format(
                '[MODULE]',
                getattr(module, '__name__', 'Unknown'),
                '[CODE]',
                error.code,
                err_name,
                '[MESSAGE]',
                error.message.replace('\n', '; '),
                '[DATA]',
                error.data,
            )

            # Add `module` attribute for `client_error`
            self.client_error.module = module

        super().__init__(error)

    @staticmethod
    def get_module(code: int) -> Tuple[Union[EnumMeta, None], str]:
        """
        Get module name and error verbose name by code

        :param code: Error code
        :return: Module class name, error verbose name
        """
        modules = [
            ClientErrorCode,
            AbiErrorCode,
            BocErrorCode,
            CryptoErrorCode,
            NetErrorCode,
            ProcessingErrorCode,
            TvmErrorCode,
            DebotErrorCode,
            ProofsErrorCode,
        ]
        for module in modules:
            if code not in list(module):
                continue
            return module, module(code).name
        return None, 'UNKNOWN'
