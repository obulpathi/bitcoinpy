from wallet import Wallet

wallet = Wallet()
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
transfered = wallet.fastwithdrawfromvault(fromaddress, toaddress, amount)
if transfered:
    print "Transfered :", transfered, " to:", toaddress
else:
    print "Sorry, an error occured"
