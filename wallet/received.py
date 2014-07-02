import sys
import bitcoinrpc
import bitcoin.utils

# JSON-RPC server user, password.  Uses HTTP Basic authentication.
rpcuser="user"
rpcpass="passwd"

address = sys.argv[1]

connection = bitcoinrpc.connect_to_remote(rpcuser, rpcpass, host='localhost', port=9333, use_https=False)
txoutlist = connection.getreceivedbyaddress(address)

for txout in txoutlist:
    print txout
