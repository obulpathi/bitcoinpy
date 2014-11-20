from wallet import Wallet

wallet = Wallet()
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
    for txouts in transaction['outputs']:
        print txouts['toaddress'] + ": ", txouts['amount']
