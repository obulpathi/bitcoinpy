import sys
import bitcoinrpc
from bitcoinrpc.exceptions import InsufficientFunds

# JSON-RPC server user, password.  Uses HTTP Basic authentication.
rpcuser="user"
rpcpass="passwd"

print sys.argv
toaddress = sys.argv[1]
amount = int(sys.argv[2])

print "Transferring: ", amount, " to: ", toaddress
connection = bitcoinrpc.connect_to_remote(rpcuser, rpcpass, host='localhost', port=9333, use_https=False)
connection.sendtoaddress(toaddress, amount)
