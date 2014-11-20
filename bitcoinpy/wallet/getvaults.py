from wallet import Wallet

wallet = Wallet()
vaults = wallet.getvaults()
for vault in vaults:
    print "Vault Address:", vault
    print "\tBalance: ", vaults[vault]['balance']
    print "\tAddress:", vaults[vault]['address']
    print "\tMaster Address:", vaults[vault]['master_address']
    print "\tReceived transactions:\n",
    if vaults[vault]['received']:
        print '\t\ttxhash:', vaults[vault]['received']['txhash'],
        print 'n:', vaults[vault]['received']['n'], 'value:', vaults[vault]['received']['value']
    else:
            print "\t\tNone"
