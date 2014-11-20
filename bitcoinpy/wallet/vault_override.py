from wallet import Wallet

wallet = Wallet()
account = wallet.getaccount()
toaddress = wallet.getnewaddress()

print ('\nPending Transfers')
transactions = wallet.getpendingtransactions()

for n, transaction in transactions.iteritems():
    print "\tId: ", n
    print "\tInputs: "
    for txin in transaction['inputs']:
        print "\t\t", txin
    print "\tOutputs: "
    for txout in transaction['outputs']:
        print "\t\t", txout

index = raw_input("Enter the id of the vault transaction you want to override: ")
fromaddress = transactions[index]['inputs'][0]
print "Fromaddress: ", fromaddress
print "Toaddress: ", toaddress
print("Overriding the transaction")
wallet.overridevault(fromaddress, toaddress)
