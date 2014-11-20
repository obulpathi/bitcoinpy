from wallet import Wallet

wallet = Wallet()
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
