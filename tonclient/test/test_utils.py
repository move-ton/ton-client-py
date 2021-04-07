import base64
import unittest

from tonclient.errors import TonException
from tonclient.test.helpers import async_core_client, sync_core_client
from tonclient.types import AddressStringFormat, ParamsOfConvertAddress, \
    ParamsOfCalcStorageFee, ParamsOfCompressZstd, ParamsOfDecompressZstd


class TestTonUtilsAsyncCore(unittest.TestCase):
    def test_convert_address(self):
        account_id = 'fcb91a3a3816d0f7b8c2c76108b8a9bc5a6b7a55bd79f8ab101c52db29232260'
        hex_ = '-1:fcb91a3a3816d0f7b8c2c76108b8a9bc5a6b7a55bd79f8ab101c52db29232260'
        hex_workchain0 = '0:fcb91a3a3816d0f7b8c2c76108b8a9bc5a6b7a55bd79f8ab101c52db29232260'
        base64 = 'Uf/8uRo6OBbQ97jCx2EIuKm8Wmt6Vb15+KsQHFLbKSMiYG+9'
        base64url = 'kf_8uRo6OBbQ97jCx2EIuKm8Wmt6Vb15-KsQHFLbKSMiYIny'

        convert_params = ParamsOfConvertAddress(
            address=account_id, output_format=AddressStringFormat.Hex())
        converted = async_core_client.utils.convert_address(
            params=convert_params)
        self.assertEqual(hex_workchain0, converted.address)

        convert_params = ParamsOfConvertAddress(
            address=converted.address,
            output_format=AddressStringFormat.AccountId())
        converted = async_core_client.utils.convert_address(
            params=convert_params)
        self.assertEqual(account_id, converted.address)

        convert_params = ParamsOfConvertAddress(
            address=hex_,
            output_format=AddressStringFormat.Base64(
                url=False, test=False, bounce=False))
        converted = async_core_client.utils.convert_address(
            params=convert_params)
        self.assertEqual(base64, converted.address)

        convert_params = ParamsOfConvertAddress(
            address=base64,
            output_format=AddressStringFormat.Base64(
                url=True, test=True, bounce=True))
        converted = async_core_client.utils.convert_address(
            params=convert_params)
        self.assertEqual(base64url, converted.address)

        convert_params = ParamsOfConvertAddress(
            address=base64url,
            output_format=AddressStringFormat.Hex())
        converted = async_core_client.utils.convert_address(
            params=convert_params)
        self.assertEqual(hex_, converted.address)

        with self.assertRaises(TonException):
            convert_params = ParamsOfConvertAddress(
                address='-1:00',
                output_format=AddressStringFormat.Hex())
            async_core_client.utils.convert_address(params=convert_params)

    def test_calc_storage_fee(self):
        account = 'te6ccgECHQEAA/wAAnfAArtKDoOR5+qId/SCUGSSS9Qc4RD86X6TnTMjmZ4e+7EyOobmQvsHNngAAAg6t/34DgJWKJuuOehjU0ADAQFBlcBqp0PR+QAN1kt1SY8QavS350RCNNfeZ+ommI9hgd/gAgBToB6t2E3E7a7aW2YkvXv2hTmSWVRTvSYmCVdH4HjgZ4Z94AAAAAvsHNwwAib/APSkICLAAZL0oOGK7VNYMPShBgQBCvSkIPShBQAAAgEgCgcBAv8IAf5/Ie1E0CDXScIBn9P/0wD0Bfhqf/hh+Gb4Yo4b9AVt+GpwAYBA9A7yvdcL//hicPhjcPhmf/hh4tMAAY4SgQIA1xgg+QFY+EIg+GX5EPKo3iP4RSBukjBw3vhCuvLgZSHTP9MfNCD4I7zyuSL5ACD4SoEBAPQOIJEx3vLQZvgACQA2IPhKI8jLP1mBAQD0Q/hqXwTTHwHwAfhHbvJ8AgEgEQsCAVgPDAEJuOiY/FANAdb4QW6OEu1E0NP/0wD0Bfhqf/hh+Gb4Yt7RcG1vAvhKgQEA9IaVAdcLP3+TcHBw4pEgjjJfM8gizwv/Ic8LPzExAW8iIaQDWYAg9ENvAjQi+EqBAQD0fJUB1ws/f5NwcHDiAjUzMehfAyHA/w4AmI4uI9DTAfpAMDHIz4cgzo0EAAAAAAAAAAAAAAAAD3RMfijPFiFvIgLLH/QAyXH7AN4wwP+OEvhCyMv/+EbPCwD4SgH0AMntVN5/+GcBCbkWq+fwEAC2+EFujjbtRNAg10nCAZ/T/9MA9AX4an/4Yfhm+GKOG/QFbfhqcAGAQPQO8r3XC//4YnD4Y3D4Zn/4YeLe+Ebyc3H4ZtH4APhCyMv/+EbPCwD4SgH0AMntVH/4ZwIBIBUSAQm7Fe+TWBMBtvhBbo4S7UTQ0//TAPQF+Gp/+GH4Zvhi3vpA1w1/ldTR0NN/39cMAJXU0dDSAN/RVHEgyM+FgMoAc89AzgH6AoBrz0DJc/sA+EqBAQD0hpUB1ws/f5NwcHDikSAUAISOKCH4I7ubIvhKgQEA9Fsw+GreIvhKgQEA9HyVAdcLP3+TcHBw4gI1MzHoXwb4QsjL//hGzwsA+EoB9ADJ7VR/+GcCASAYFgEJuORhh1AXAL74QW6OEu1E0NP/0wD0Bfhqf/hh+Gb4Yt7U0fhFIG6SMHDe+EK68uBl+AD4QsjL//hGzwsA+EoB9ADJ7VT4DyD7BCDQ7R7tU/ACMPhCyMv/+EbPCwD4SgH0AMntVH/4ZwIC2hsZAQFIGgAs+ELIy//4Rs8LAPhKAfQAye1U+A/yAAEBSBwAWHAi0NYCMdIAMNwhxwDcIdcNH/K8UxHdwQQighD////9vLHyfAHwAfhHbvJ8'
        params = ParamsOfCalcStorageFee(account=account, period=1000)
        result = async_core_client.utils.calc_storage_fee(params=params)
        self.assertEqual('330', result.fee)

    def test_compression(self):
        uncompressed = 'Lorem ipsum dolor sit amet, consectetur adipiscing ' \
                       'elit, sed do eiusmod tempor incididunt ut labore et ' \
                       'dolore magna aliqua. Ut enim ad minim veniam, quis ' \
                       'nostrud exercitation ullamco laboris nisi ut aliquip '\
                       'ex ea commodo consequat. Duis aute irure dolor in ' \
                       'reprehenderit in voluptate velit esse cillum dolore ' \
                       'eu fugiat nulla pariatur. Excepteur sint occaecat ' \
                       'cupidatat non proident, sunt in culpa qui officia ' \
                       'deserunt mollit anim id est laborum.'
        uncompressed = base64.b64encode(uncompressed.encode()).decode()

        compressed = async_core_client.utils.compress_zstd(
            params=ParamsOfCompressZstd(uncompressed=uncompressed, level=21))
        self.assertEqual(
            'KLUv/QCAdQgAJhc5GJCnsA2AIm2tVzjno88mHb3Ttx9b8fXHHDAAMgAyAMUsVo6Pi3rPTDF2WDl510aHTwt44hrUxbn5oF6iUfiUiRbQhYo/PSM2WvKYt/hMIOQmuOaY/bmJQoRky46EF+cEd+Thsep5Hloo9DLCSwe1vFwcqIHycEKlMqBSo+szAiIBhkukH5kSIVlFukEWNF2SkIv6HBdPjFAjoUliCPjzKB/4jK91X95rTAKoASkPNqwUEw2Gkscdb3lR8YRYOR+P0sULCqzPQ8mQFJWnBSyP25mWIY2bFEUSJiGsWD+9NBqLhIAGDggQkLMbt5Y1aDR4uLKqwJXmQFPg/XTXIL7LCgspIF1YYplND4Uo',
            compressed.compressed)

        decompressed = async_core_client.utils.decompress_zstd(
            params=ParamsOfDecompressZstd(compressed=compressed.compressed))
        self.assertEqual(uncompressed, decompressed.decompressed)


class TestTonUtilsSyncCore(unittest.TestCase):
    """ Sync core is not recommended to use """
    def test_convert_address(self):
        account_id = 'fcb91a3a3816d0f7b8c2c76108b8a9bc5a6b7a55bd79f8ab101c52db29232260'
        hex_ = '-1:fcb91a3a3816d0f7b8c2c76108b8a9bc5a6b7a55bd79f8ab101c52db29232260'
        hex_workchain0 = '0:fcb91a3a3816d0f7b8c2c76108b8a9bc5a6b7a55bd79f8ab101c52db29232260'
        base64 = 'Uf/8uRo6OBbQ97jCx2EIuKm8Wmt6Vb15+KsQHFLbKSMiYG+9'
        base64url = 'kf_8uRo6OBbQ97jCx2EIuKm8Wmt6Vb15-KsQHFLbKSMiYIny'

        convert_params = ParamsOfConvertAddress(
            address=account_id, output_format=AddressStringFormat.Hex())
        converted = sync_core_client.utils.convert_address(
            params=convert_params)
        self.assertEqual(hex_workchain0, converted.address)

        convert_params = ParamsOfConvertAddress(
            address=converted.address,
            output_format=AddressStringFormat.AccountId())
        converted = sync_core_client.utils.convert_address(
            params=convert_params)
        self.assertEqual(account_id, converted.address)

        convert_params = ParamsOfConvertAddress(
            address=hex_,
            output_format=AddressStringFormat.Base64(
                url=False, test=False, bounce=False))
        converted = sync_core_client.utils.convert_address(
            params=convert_params)
        self.assertEqual(base64, converted.address)

        convert_params = ParamsOfConvertAddress(
            address=base64,
            output_format=AddressStringFormat.Base64(
                url=True, test=True, bounce=True))
        converted = sync_core_client.utils.convert_address(
            params=convert_params)
        self.assertEqual(base64url, converted.address)

        convert_params = ParamsOfConvertAddress(
            address=base64url,
            output_format=AddressStringFormat.Hex())
        converted = sync_core_client.utils.convert_address(
            params=convert_params)
        self.assertEqual(hex_, converted.address)

        with self.assertRaises(TonException):
            convert_params = ParamsOfConvertAddress(
                address='-1:00',
                output_format=AddressStringFormat.Hex())
            sync_core_client.utils.convert_address(params=convert_params)
