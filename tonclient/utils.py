"""Utils module methods"""
from typing import Union, Awaitable

from tonclient.module import TonModule
from tonclient.types import (
    ParamsOfConvertAddress,
    ResultOfConvertAddress,
    ParamsOfCalcStorageFee,
    ResultOfCalcStorageFee,
    ParamsOfCompressZstd,
    ResultOfCompressZstd,
    ParamsOfDecompressZstd,
    ResultOfDecompressZstd,
    ParamsOfGetAddressType,
    ResultOfGetAddressType,
)


class TonUtils(TonModule):
    """Free TON utils SDK API implementation"""

    def convert_address(
        self, params: ParamsOfConvertAddress
    ) -> Union[ResultOfConvertAddress, Awaitable[ResultOfConvertAddress]]:
        """
        Converts address from any TON format to any TON format

        :param params: See `types.ParamsOfConvertAddress`
        :return: See `types.ResultOfConvertAddress`
        """
        response = self.request(method='utils.convert_address', **params.dict)
        return self.response(classname=ResultOfConvertAddress, response=response)

    def calc_storage_fee(
        self, params: ParamsOfCalcStorageFee
    ) -> Union[ResultOfCalcStorageFee, Awaitable[ResultOfCalcStorageFee]]:
        """
        Calculates storage fee for an account over a specified time period

        :param params: See `types.ParamsOfCalcStorageFee`
        :return: See `types.ResultOfCalcStorageFee`
        """
        response = self.request(method='utils.calc_storage_fee', **params.dict)
        return self.response(classname=ResultOfCalcStorageFee, response=response)

    def compress_zstd(
        self, params: ParamsOfCompressZstd
    ) -> Union[ResultOfCompressZstd, Awaitable[ResultOfCompressZstd]]:
        """
        Compresses data using Zstandard algorithm

        :param params: See `types.ParamsOfCompressZstd`
        :return: See `types.ResultOfCompressZstd`
        """
        response = self.request(method='utils.compress_zstd', **params.dict)
        return self.response(classname=ResultOfCompressZstd, response=response)

    def decompress_zstd(
        self, params: ParamsOfDecompressZstd
    ) -> Union[ResultOfDecompressZstd, Awaitable[ResultOfDecompressZstd]]:
        """
        Decompresses data using Zstandard algorithm

        :param params: See `types.ParamsOfDecompressZstd`
        :return: See `types.ResultOfDecompressZstd`
        """
        response = self.request(method='utils.decompress_zstd', **params.dict)
        return self.response(classname=ResultOfDecompressZstd, response=response)

    def get_address_type(
        self, params: ParamsOfGetAddressType
    ) -> Union[ResultOfGetAddressType, Awaitable[ResultOfGetAddressType]]:
        """
        Validates and returns the type of any TON address.

        Address types are the following:
        `0:919db8e740d50bf349df2eea03fa30c385d846b991ff5542e67098ee833fc7f7`
        standart TON address most commonly used in all cases.
        Also called as hex address
        `919db8e740d50bf349df2eea03fa30c385d846b991ff5542e67098ee833fc7f7` -
        account ID. A part of full address. Identifies account inside
        particular workchain `EQCRnbjnQNUL80nfLuoD+jDDhdhGuZH/VULmcJjugz/H9wam`
        base64 address. Also called "user-friendly". Was used at the
        beginning of TON. Now it is supported for compatibility

        :param params: See `types.ParamsOfGetAddressType`
        :return: See `types.ResultOfGetAddressType`
        """
        response = self.request(method='utils.get_address_type', **params.dict)
        return self.response(classname=ResultOfGetAddressType, response=response)
