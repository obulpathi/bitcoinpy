import sys
import argparse

from bitcoinpy.wallet.wallet import Wallet
from bitcoinpy import bitcoinrpc
from bitcoinpy.bitcoinrpc.exceptions import TransportException
from bitcoinpy.version import VERSION, COPYRIGHT_YEAR

def info(wallet):

    info = wallet.getinfo()
    print "Blocks:", info.blocks

def newaddress(wallet):

    address = wallet.getnewaddress()
    print address

def account(wallet):

    account = wallet.getaccount()

    for subaccount in account.itervalues():
        print "Address: ", subaccount['address']
        print "Public key: ", subaccount['public_key']
        print "Private key: ", subaccount['private_key']
        print "Balance: ", subaccount['balance']
        print "\n\n"

def balance(wallet):

    account = wallet.getaccount()

    print ('\nAccounts')
    for subaccount in account.itervalues():
        print subaccount['address']  + ": ", subaccount['balance']

def blockchain(wallet):
    wallet.dumpblockchain()

def mempool(wallet):
    wallet.dumpmempool()

def received(wallet):
    address = raw_input("Enter the address to check received transactions: ")
    txouts = wallet.received(address)
    for count, txhash in enumerate(txouts):
        print count
        print "\ttxhash: ", txouts[txhash]['txhash']
        print "\tn: ", txouts[txhash]['n']
        print "\tvalue: ", txouts[txhash]['value']

def send(wallet):
    account = wallet.getaccount()

    toaddress = raw_input("Enter the address to send coins to: ")
    amount = int(input("Enter the balance to transfer to address: "))

    balance = 0
    for subaccount in account.itervalues():
        balance = balance + subaccount['balance']

    if balance < amount:
        print("Not enough balance")
        exit(1)

    print "Transferring: ", amount, " \tto: ", toaddress
    wallet.connection.sendtoaddress(toaddress, amount)

def run(args):
    try:
        wallet = Wallet(config_file=args.config_file)
        globals()[args.command](wallet)
    except TransportException as e:
        print str(e)
        sys.exit(1)

    sys.exit(0)

# any function added above should be registered here
_SUPPORTED_COMMANDS = [
    ("account", "Look at the account summary.",),
    ("balance", "Current wallet balance.",),
    ("blockchain", "Dump the current block chain.",),
    ("info", "Get basic info",),
    ("mempool", "Dump the mempool.",),
    ("newaddress", "Generate a new address.",),
    ("received", "Received transactions.",),
    ("send", "Send coins to normal address.",),
    ]

_EPILOG = "Commands Desription:\n====================\n"
for cmd, hlp in _SUPPORTED_COMMANDS:
    _EPILOG += "{:<30} {}\n".format(cmd, hlp)

_EPILOG += """
In addition, you can pass in the config-file to be used.
By default, it is ~/.reversecoin.cfg
"""

_WALLET_NAME = """
Walletpy - v%s

Copyright: %s
""" % (VERSION, COPYRIGHT_YEAR)

def parse_arguments():

    parser = argparse.ArgumentParser(description=_WALLET_NAME,
                                     epilog=_EPILOG,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=[c for c,_ in _SUPPORTED_COMMANDS])
    parser.add_argument("config_file", nargs='?', default='~/.bitcoinpy.cfg')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    return parser.parse_args()

def main():
    args = parse_arguments()
    run(args)

if __name__ == "__main__":
    main()
