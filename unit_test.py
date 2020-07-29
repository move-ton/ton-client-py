import unittest
import lib
class TestTonClient(unittest.TestCase):

  def test_version(self):
      client = lib.TonClient()
      self.assertEqual(client.version()["result"], lib.LIB_VERSION)

if __name__ == '__main__':
    unittest.main()