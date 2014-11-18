import os
import time
import unittest

from tests.api import utils
from bitcoinpy import bitcoinrpc


class TestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        bitcoinpyd = utils.BitcoinpyDaemon()
        miner = utils.BitcoinpyMiner()
        bitcoinpyd.start()
        miner.start()
        time.sleep(3)

    def setUp(self):
        rpcuser = "user"
        rpcpass = "passwd"
        self.account = "account"
        self.connection = bitcoinrpc.connect_to_remote(
            rpcuser, rpcpass, host='localhost', port=9333, use_https=False)

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        os.system("killall -9 minerpy > /dev/null 2>&1");
        os.system("killall -9 bitcoinpy > /dev/null 2>&1");
        time.sleep(1)
