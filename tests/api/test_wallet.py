import os
import sys
import subprocess
import random
import time
import unittest

from tests.api import base
from tests.api import utils
from bitcoinpy import bitcoinrpc

class TestWallet(base.TestBase):

    def test_account(self):
        account = self.connection.getaccount(self.account)
        self.assertIsInstance(account, dict)
        for subaccount in account.itervalues():
            self.assertIn('address', subaccount)
            self.assertIn('public_key', subaccount)
            self.assertIn('private_key', subaccount)
            self.assertIn('balance', subaccount)

    def test_info(self):
        # wait until blocks are generated
        info = utils.wait_until_blocks_are_generated(self.connection)
        self.assertTrue(info.blocks >= -1)

    def test_newaddress(self):
        address = self.connection.getnewaddress()
        self.assertIsNotNone(address)

    def test_send(self):
        # wait until blocks are generated
        info = utils.wait_until_blocks_are_generated(self.connection)
        self.assertTrue(info.blocks >= -1)

        # generate a new toaddress
        toaddress = self.connection.getnewaddress()
        amount = random.randint(20, 30)
        self.connection.sendtoaddress(toaddress, amount)

        account = self.connection.getaccount(self.account)
        self.assertIn(toaddress, account)

        # wait for account to get updated
        subaccount = utils.wait_until_account_has_balance(self.connection, toaddress)
        self.assertEqual(int(subaccount['balance']), amount)

    def test_double_send(self):
        # wait until 10 blocks are generated
        info = utils.wait_until_n_blocks_are_generated(self.connection, 10)
        self.assertTrue(info.blocks >= 10)

        # generate a new toaddress
        toaddress1 = self.connection.getnewaddress()
        toaddress2 = self.connection.getnewaddress()
        amount = utils.get_total_balance(self.connection) - 1
        transfered1 = self.connection.sendtoaddress(toaddress1, amount)
        transfered2 = self.connection.sendtoaddress(toaddress2, amount)
        self.assertEqual(amount, transfered1)
        self.assertEqual(amount, transfered2)

        # wait for one of the accounts to get updated
        while True:
            utils.wait_until_n_more_blocks_are_generated(self.connection, 1)
            account = self.connection.getaccount(self.account)
            subaccount1 = account[toaddress1]
            subaccount2 = account[toaddress2]
            if subaccount1['balance'] or subaccount2['balance']:
                balance_max = max(subaccount1['balance'], subaccount2['balance'])
                balance_min = min(subaccount1['balance'], subaccount2['balance'])
                self.assertEqual(int(balance_max), amount)
                self.assertEqual(int(balance_min), 0)
                break
