import unittest

from tonclient.errors import TonException
from tonclient.test.helpers import async_core_client, sync_core_client
from tonclient.types import AddressStringFormat, ParamsOfConvertAddress


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
