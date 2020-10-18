import unittest

from tonclient.errors import TonException
from tonclient.test.helpers import async_core_client, sync_core_client
from tonclient.types import AddressStringFormat


class TestTonUtilsAsyncCore(unittest.TestCase):
    def test_convert_address(self):
        account_id = 'fcb91a3a3816d0f7b8c2c76108b8a9bc5a6b7a55bd79f8ab101c52db29232260'
        hex_ = '-1:fcb91a3a3816d0f7b8c2c76108b8a9bc5a6b7a55bd79f8ab101c52db29232260'
        hex_workchain0 = '0:fcb91a3a3816d0f7b8c2c76108b8a9bc5a6b7a55bd79f8ab101c52db29232260'
        base64 = 'Uf/8uRo6OBbQ97jCx2EIuKm8Wmt6Vb15+KsQHFLbKSMiYG+9'
        base64url = 'kf_8uRo6OBbQ97jCx2EIuKm8Wmt6Vb15-KsQHFLbKSMiYIny'

        converted = async_core_client.utils.convert_address(
            address=account_id, output_format=AddressStringFormat.Hex)
        self.assertEqual(hex_workchain0, converted)

        converted = async_core_client.utils.convert_address(
            address=converted, output_format=AddressStringFormat.AccountId)
        self.assertEqual(account_id, converted)

        converted = async_core_client.utils.convert_address(
            address=hex_, output_format=AddressStringFormat.base64())
        self.assertEqual(base64, converted)

        converted = async_core_client.utils.convert_address(
            address=base64, output_format=AddressStringFormat.base64(
                url=True, test=True, bounce=True))
        self.assertEqual(base64url, converted)

        converted = async_core_client.utils.convert_address(
            address=base64url, output_format=AddressStringFormat.Hex)
        self.assertEqual(hex_, converted)

        with self.assertRaises(TonException):
            async_core_client.utils.convert_address(
                address='-1:00', output_format=AddressStringFormat.Hex)


class TestTonUtilsSyncCore(unittest.TestCase):
    """ Sync core is not recommended to use """
    def test_convert_address(self):
        account_id = 'fcb91a3a3816d0f7b8c2c76108b8a9bc5a6b7a55bd79f8ab101c52db29232260'
        hex_ = '-1:fcb91a3a3816d0f7b8c2c76108b8a9bc5a6b7a55bd79f8ab101c52db29232260'
        hex_workchain0 = '0:fcb91a3a3816d0f7b8c2c76108b8a9bc5a6b7a55bd79f8ab101c52db29232260'
        base64 = 'Uf/8uRo6OBbQ97jCx2EIuKm8Wmt6Vb15+KsQHFLbKSMiYG+9'
        base64url = 'kf_8uRo6OBbQ97jCx2EIuKm8Wmt6Vb15-KsQHFLbKSMiYIny'

        converted = sync_core_client.utils.convert_address(
            address=account_id, output_format=AddressStringFormat.Hex)
        self.assertEqual(hex_workchain0, converted)

        converted = sync_core_client.utils.convert_address(
            address=converted, output_format=AddressStringFormat.AccountId)
        self.assertEqual(account_id, converted)

        converted = sync_core_client.utils.convert_address(
            address=hex_, output_format=AddressStringFormat.base64())
        self.assertEqual(base64, converted)

        converted = sync_core_client.utils.convert_address(
            address=base64, output_format=AddressStringFormat.base64(
                url=True, test=True, bounce=True))
        self.assertEqual(base64url, converted)

        converted = sync_core_client.utils.convert_address(
            address=base64url, output_format=AddressStringFormat.Hex)
        self.assertEqual(hex_, converted)

        with self.assertRaises(TonException):
            sync_core_client.utils.convert_address(
                address='-1:00', output_format=AddressStringFormat.Hex)
