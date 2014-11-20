import sys
import argparse

from reversecoin.wallet.wallet import Wallet
from reversecoin import bitcoinrpc
from reversecoin.bitcoinrpc.exceptions import TransportException
from reversecoin.version import VERSION, COPYRIGHT_YEAR

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

    print ('\nVaults')
    vaults = wallet.getvaults()
    for vault in vaults.itervalues():
        print vault['name']  + ": ", vault['balance']

    print ('\nPending Transfers')
    transactions = wallet.getpendingtransactions()
    for transaction in transactions.itervalues():
        fromaddress = transaction['inputs'][0]
        for txouts in transaction['outputs']:
            print fromaddress, "->", txouts['toaddress'] + ": ", txouts['amount']

def getvaults(wallet):

    vaults = wallet.getvaults()
    for vault in vaults:
        print "Vault Address:", vault
        print "\tBalance: ", vaults[vault]['balance']
        print "\tAddress:", vaults[vault]['address']
        print "\tMaster Address:", vaults[vault]['master_address']
        print "\ttimeout:", vaults[vault]['timeout']
        print "\tReceived transactions:\n",
        if vaults[vault]['received']:
            print '\t\ttxhash:', vaults[vault]['received']['txhash'],
            print 'n:', vaults[vault]['received']['n'], 'value:', vaults[vault]['received']['value']
        else:
                print "\t\tNone"

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

def savings(wallet):

    vaults = wallet.getvaults()
    for vault in vaults:
        print vault  + ": ", vaults[vault]['balance']

def vault_new(wallet):

    account = wallet.getaccount()

    toaddress = wallet.getnewaddress()
    tomaster_address = wallet.getnewaddress()
    timeout = 20
    maxfees = 10

    print("Creating new vault: address: %s master_address: %s" % \
         (toaddress, tomaster_address))
    vault_address = wallet.newvault(toaddress, tomaster_address, timeout, maxfees)

    if vault_address:
        print("Created: {0}".format(vault_address))
    else:
        print("An error occured while creating vault")

def vault_send(wallet):

    account = wallet.getaccount()

    balance = 0
    for subaccount in account.itervalues():
        balance = balance + subaccount['balance']

    vaults = wallet.getvaults()
    emptyvaults = {}
    for vault in vaults:
        if not vaults[vault]['balance']:
            emptyvaults[vault] = vaults[vault]

    vaults = emptyvaults
    vault_names = [vault for vault in vaults]
    for count, vault in enumerate(vault_names):
        print count, ":", vault + " ", vaults[vault]['balance']

    choice = int(input("Select the vault to transfer money to: "))
    if choice < 0 or choice > len(vaults)-1:
        print("Invalid choice")
        exit(1)

    vault_address = vault_names[choice]

    amount = int(input("Enter the balance to transfer to vault: "))

    if balance < amount:
        print("Not enough balance")
        exit(1)

    print("Transfering %d to vault %s" % (amount, vault_address))
    ret_value = wallet.sendtovault(vault_address, amount)
    if not ret_value:
        print("An error occured while trasfering")

def vault_withdraw(wallet):

    account = wallet.getaccount()
    toaddress = wallet.getnewaddress()

    print("Available vaults")
    vaults = wallet.getvaults()
    for n, vault in enumerate(vaults.itervalues()):
        print "Id: ", n, vault['name']  + ": ", vault['balance']
    index = int(input("Enter the id of the vault you want to transfer balance from: "))

    for n, vault in enumerate(vaults.itervalues()):
        if index == n:
            fromaddress = vault['name']

    amount = int(input("Enter the balance to transfer from: {}: ".format(fromaddress)))
    if vaults[fromaddress]['balance'] < amount + 2:
        print("In sufficient balance in vault, quitting")
        exit(2)

    print("Transfering: " + str(amount) + "\tfrom address: " + fromaddress + "\tto address: " + toaddress)
    wallet.withdrawfromvault(fromaddress, toaddress, amount)

def vault_override(wallet):

    account = wallet.getaccount()
    toaddress = wallet.getnewaddress()

    print ('\nPending Transfers')
    transactions = wallet.getpendingtransactions()

    for n, transaction in transactions.iteritems():
        print "\tId: ", n
        print "\t\tInput:", transaction['inputs'][0]
        print "\t\tOutputs: "
        for txout in transaction['outputs']:
            print "\t\t\t", txout['amount'], "->", txout['toaddress']

    index = raw_input("Enter the id of the vault transaction you want to override: ")
    fromaddress = transactions[index]['inputs'][0]
    print "Fromaddress: ", fromaddress
    print "Toaddress: ", toaddress
    print("Overriding the transaction")
    wallet.overridevault(fromaddress, toaddress)

def vault_fast_withdraw(wallet):

    toaddress = wallet.getnewaddress()

    print("Available vaults")
    vaults = wallet.getvaults()
    vaults = list(vaults.itervalues())
    for n, vault in enumerate(vaults):
        print "Id: ", n, vault['name']  + ": ", vault['balance']
    index = int(input("Enter the id of the vault you want to transfer balance from: "))
    fromaddress = vaults[index]['name']
    amount = int(input("Enter the balance to transfer from: {}: ".format(fromaddress)))
    if vaults[index]['balance'] < amount + 2:
        print("In sufficient balance in vault, quitting")
        exit(2)

    print("Transfering: " + str(amount) + "\tfrom address: " + fromaddress + "\tto address: " + toaddress)
    wallet.fastwithdrawfromvault(fromaddress, toaddress, amount)

def vault_pending(wallet):

    account = wallet.getaccount()

    print ('\nPending Transfers')
    transactions = wallet.getpendingtransactions()

    for n, transaction in transactions.iteritems():
        print "\tId: ", n
        print "\t\tInput:", transaction['inputs'][0]
        print "\t\tOutputs: "
        for txout in transaction['outputs']:
            print "\t\t\t", txout['amount'], "->", txout['toaddress']


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
    ("getvaults", "Detailed information about the vaults.",),
    ("blockchain", "Dump the current block chain.",),
    ("info", "Get basic info",),
    ("mempool", "Dump the mempool.",),
    ("newaddress", "Generate a new address.",),
    ("received", "Received transactions.",),
    ("send", "Send coins to normal address.",),
    ("savings", "Balance in each vault account.",),
    ("vault_new", "Create a new vault account"),
    ("vault_send", "Send to a vault.",),
    ("vault_withdraw", "Withdraw from a vault.",),
    ("vault_override", "Override a vault transaction.",),
    ("vault_fast_withdraw", "Withdraw from a vault immediately. No timeout associated.",),
    ("vault_pending", "List of pending vault transactions.",),
    ]

_EPILOG = "Commands Desription:\n====================\n"
for cmd, hlp in _SUPPORTED_COMMANDS:
    _EPILOG += "{:<30} {}\n".format(cmd, hlp)

_EPILOG += """
In addition, you can pass in the config-file to be used.
By default, it is ~/.reversecoin.cfg
"""

_WALLET_NAME = """
ReverseCoin Wallet - v%s

Copyright: %s
""" % (VERSION, COPYRIGHT_YEAR)

def parse_arguments():

    parser = argparse.ArgumentParser(description=_WALLET_NAME,
                                     epilog=_EPILOG,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=[c for c,_ in _SUPPORTED_COMMANDS])
    parser.add_argument("config_file", nargs='?', default='~/.reversecoin.cfg')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    return parser.parse_args()

def main():
    args = parse_arguments()
    run(args)

if __name__ == "__main__":
    main()
