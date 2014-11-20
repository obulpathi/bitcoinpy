import sys
import os
import re

from bitcoinpy import bitcoinrpc

class Wallet(object):
    def __init__(self, config_file="~/.bitcoinpy.cfg"):
        # check if configuration file exists
        if not os.path.isfile(os.path.expanduser(config_file)):
            print('No configuration file: {0}'.format(config_file))
            sys.exit(1)

        settings = {}
        f = open(os.path.expanduser(config_file))
        for line in f:
            m = re.search('^(\w+)\s*=\s*(\S.*)$', line)
            if m is None:
                continue
            settings[m.group(1)] = m.group(2)
        f.close()

        if ('rpcuser' not in settings or
            'rpcpass' not in settings):
            print('rpcuser/rpcpass missing in the config file - {}'.format(config_file))
            sys.exit(1)

        rpcuser = settings['rpcuser']
        rpcpass = settings['rpcpass']
        account = "account"
        self.connection = bitcoinrpc.connect_to_remote(
            rpcuser, rpcpass, host='localhost', port=9333, use_https=False)

    def dumpblockchain(self):
        self.connection.dumpblockchain()

    def dumpmempool(self):
        self.connection.dumpmempool()

    def getaccount(self, account = "account"):
        account = self.connection.getaccount(account)
        return account

    def getinfo(self):
        info = self.connection.getinfo()
        return info

    def getnewaddress(self, account = "account"):
        address = self.connection.getnewaddress(account)
        return address

    def getpendingtransactions(self):
        return self.connection.getpendingtransactions()

    def received(self, address):
        return self.connection.getreceivedbyaddress(address)

    def send(self, toaddress, amount):
        self.connection.sendtoaddress(toaddress, amount)
