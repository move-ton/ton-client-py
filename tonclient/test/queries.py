import unittest
import logging

from tonclient.client import TonClient, DEVNET_BASE_URL
from tonclient.errors import TonException
from tonclient.queries import TonQueryBuilder

logger = logging.getLogger("TonQueriesTest")
client = TonClient(servers=[DEVNET_BASE_URL])


class TestQueries(unittest.TestCase):
    def test_query(self):
        query = TonQueryBuilder(table="messages")\
            .filter(dst__eq="0:668b5c83056ebf1852cc7af4e61c8a421056c0311f035a39e5baf7ce28b14728")\
            .result("id", "msg_type", "status")\
            .order("created_at")\
            .limit(1)

        result = client.queries.query(query=query)
        self.assertEqual(result[0]["id"], "6b4c494933f78e21de45646066b4a954d642f229de2c2c0237c5063358e29399")

    def test_wait_for(self):
        query = TonQueryBuilder(table="accounts")\
            .filter(id__eq="0:668b5c83056ebf1852cc7af4e61c8a421056c0311f035a39e5baf7ce28b14728")\
            .result("balance")

        result = client.queries.wait_for(query=query, timeout=5)
        self.assertGreater(int(result["balance"], 16), 0)

        def __callable():
            client.queries.wait_for(query=query, timeout=-1)
        self.assertRaises(TonException, __callable)

    def test_subscribe(self):
        # Subscribe for query
        query = TonQueryBuilder(table="blocks")\
            .filter(workchain_id__eq=0)\
            .result("id", "gen_utime").order("gen_utime")
        handle = client.queries.subscribe(query=query)

        # Get query.next
        for i in range(5):
            logger.warning(client.queries.get_next(handle=handle))

        # Unsubscribe
        client.queries.unsubscribe(handle=handle)
