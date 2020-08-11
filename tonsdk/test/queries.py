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
        self.assertGreater(int(result["result"][0]["balance"], 16), 0)
