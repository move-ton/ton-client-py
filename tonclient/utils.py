from tonclient.decorators import result_as
from tonclient.module import TonModule
from tonclient.types import ParamsOfConvertAddress, ResultOfConvertAddress, \
    ParamsOfCalcStorageFee, ResultOfCalcStorageFee


class TonUtils(TonModule):
    """ Free TON utils SDK API implementation """
    @result_as(classname=ResultOfConvertAddress)
    def convert_address(
            self, params: ParamsOfConvertAddress) -> ResultOfConvertAddress:
        """
        Converts address from any TON format to any TON format
        :param params: See `types.ParamsOfConvertAddress`
        :return: See `types.ResultOfConvertAddress`
        """
        return self.request(method='utils.convert_address', **params.dict)

    @result_as(classname=ResultOfCalcStorageFee)
    def calc_storage_fee(
            self, params: ParamsOfCalcStorageFee) -> ResultOfCalcStorageFee:
        """
        Calculates storage fee for an account over a specified time period
        :param params: See `types.ParamsOfCalcStorageFee`
        :return: See `types.ResultOfCalcStorageFee`
        """
        return self.request(method='utils.calc_storage_fee', **params.dict)
