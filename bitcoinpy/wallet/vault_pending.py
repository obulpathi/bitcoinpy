from wallet import Wallet

wallet = Wallet()
account = wallet.getaccount()

print ('\nPending Transfers')
transactions = wallet.getpendingtransactions()
for transaction in transactions:
    for txouts in transaction['outputs']:
        print txouts['toaddress'] + ": ", txouts['amount']
