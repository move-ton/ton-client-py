import unittest
from datetime import datetime

from tonclient.client import TonClient, DEVNET_BASE_URL
from tonclient.errors import TonException
from tonclient.net import TonQLQuery

client = TonClient(network={'server_address': DEVNET_BASE_URL})


class TestTonNet(unittest.TestCase):
    def test_query_collection(self):
        query = TonQLQuery(collection='blocks_signatures') \
            .set_result('id').set_limit(1)
        result = client.net.query_collection(query=query)
        self.assertGreater(len(result), 0)

        query = TonQLQuery(collection='accounts').set_result('id', 'balance') \
            .set_limit(5)
        result = client.net.query_collection(query=query)
        self.assertEqual(5, len(result))

        query = TonQLQuery(collection='messages') \
            .set_filter(created_at__gt=1562342740) \
            .set_result('body created_at').set_order('created_at') \
            .set_limit(10)
        result = client.net.query_collection(query=query)
        self.assertGreater(result[0]['created_at'], 1562342740)

        with self.assertRaises(TonException):
            query = TonQLQuery(collection='messages')
            client.net.query_collection(query=query)

    def test_wait_for_collection(self):
        now = int(datetime.now().timestamp())
        query = TonQLQuery(collection='transactions') \
            .set_filter(now__gt=now).set_result('id now')
        result = client.net.wait_for_collection(query=query)
        self.assertGreater(result['now'], now)

        with self.assertRaises(TonException):
            client.net.wait_for_collection(query=query, timeout=1)

    def test_unsubscribe(self):
        client.net.unsubscribe(handle=100000)
