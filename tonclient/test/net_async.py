from datetime import datetime

import aiounittest

from tonclient.errors import TonException
from tonclient.net import TonQLQuery
from tonclient.test.net import client

client.is_async = True


class TestTonNetAsync(aiounittest.AsyncTestCase):
    async def test_query_collection(self):
        query = TonQLQuery(collection='blocks_signatures') \
            .set_result('id').set_limit(1)
        result = await client.net.query_collection(query=query)
        self.assertGreater(len(result), 0)

        query = TonQLQuery(collection='accounts').set_result('id', 'balance') \
            .set_limit(5)
        result = await client.net.query_collection(query=query)
        self.assertEqual(5, len(result))

        query = TonQLQuery(collection='messages') \
            .set_filter(created_at__gt=1562342740) \
            .set_result('body created_at').set_order('created_at') \
            .set_limit(10)
        result = await client.net.query_collection(query=query)
        self.assertGreater(result[0]['created_at'], 1562342740)

        with self.assertRaises(TonException):
            query = TonQLQuery(collection='messages')
            await client.net.query_collection(query=query)

    async def test_wait_for_collection(self):
        now = int(datetime.now().timestamp())
        query = TonQLQuery(collection='transactions') \
            .set_filter(now__gt=now).set_result('id now')
        result = await client.net.wait_for_collection(query=query)
        self.assertGreater(result['now'], now)

        with self.assertRaises(TonException):
            await client.net.wait_for_collection(query=query, timeout=1)

    async def test_unsubscribe(self):
        await client.net.unsubscribe(handle=100000)
