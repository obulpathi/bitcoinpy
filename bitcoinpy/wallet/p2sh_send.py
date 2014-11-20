import sys
import bitcoinrpc
from bitcoinrpc.exceptions import InsufficientFunds

# JSON-RPC server user, password.  Uses HTTP Basic authentication.
rpcuser="user"
rpcpass="passwd"

print sys.argv
pubkey = sys.argv[1]
mpubkey = sys.argv[2]
timeout = int(sys.argv[3])
amount = int(sys.argv[4])

def vault_script(pubkey, mpubkey, timeout, amount):
	OPCODE_VAULT = "VAULT"
	return OPCODE_VAULT + hash(pubkey + mpubkey + timeout + amount)

toaddress = vault_script(pubkey, mpubkey, timeout, amount)
print "Transferring: ", amount, " to: ", toaddress
connection = bitcoinrpc.connect_to_remote(rpcuser, rpcpass, host='localhost', port=9333, use_https=False)
connection.sendtoaddress(toaddress, amount)
