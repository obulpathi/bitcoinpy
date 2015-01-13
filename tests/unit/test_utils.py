import unittest

from bitcoinpy.lib import utils

class TestUtils(unittest.TestCase):
    def setUp(self):
        pass

    def test_public_key_to_address(self):
        public_key, private_key, address = utils.getnewaddress()
        myaddress = utils.public_key_to_address(public_key)
        self.assertEqual(address, myaddress)

if __name__ == '__main__':
    unittest.main()
