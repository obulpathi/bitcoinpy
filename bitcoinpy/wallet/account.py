from wallet import Wallet

wallet = Wallet()
account = wallet.getaccount()

for subaccount in account.itervalues():
    print "Address: ", subaccount['address']
    print "Public key: ", subaccount['public_key']
    print "Private key: ", subaccount['private_key']
    print "Balance: ", subaccount['balance']
    print "\n\n"
