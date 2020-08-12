import unittest

from tonsdk.lib import TonClient, DEVNET_BASE_URL

CLIENT = TonClient(servers=[DEVNET_BASE_URL])


class TestQueries(unittest.TestCase):
    def test_query(self):
        filter = {
            "id": {
                "eq": "0:668b5c83056ebf1852cc7af4e61c8a421056c0311f035a39e5baf7ce28b14728"
            }
        }

        result = CLIENT.query(
            table="accounts", filter=filter, result="balance")
        self.assertGreater(int(result[0]["balance"], 16), 0)

    def test_query_wait_for(self):
        filter = {
            "id": {
                "eq": "0:668b5c83056ebf1852cc7af4e61c8a421056c0311f035a39e5baf7ce28b14728"
            }
        }

        result = CLIENT.query(
            table="accounts", filter=filter, result="balance")
        self.assertGreater(int(result[0]["balance"], 16), 0)

    def test_query_subscribe(self):
        # Subscribe for query
        table = "blocks"
        condition = {"workchain_id": {"eq": 0}}
        result = "id gen_utime"

        handle = CLIENT.query_subscribe(
            table=table, filter=condition, result=result)

        # Get query.next
        for i in range(5):
            print(CLIENT.query_get_next(handle=handle))

        # Unsubscribe
        CLIENT.query_unsubscribe(handle=handle)
