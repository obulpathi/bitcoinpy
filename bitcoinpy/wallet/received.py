import sys
import bitcoinrpc

# JSON-RPC server user, password.  Uses HTTP Basic authentication.
rpcuser="user"
rpcpass="passwd"

address = raw_input("Enter the address to check received transactions: ")

connection = bitcoinrpc.connect_to_remote(rpcuser, rpcpass, host='localhost', port=9333, use_https=False)
txoutlist = connection.getreceivedbyaddress(address)

for count, txhash in enumerate(txouts):
    print count
    print "\ttxhash: ", txouts[txhash]['txhash']
    print "\tn: ", txouts[txhash]['n']
    print "\tvalue: ", txouts[txhash]['value']
