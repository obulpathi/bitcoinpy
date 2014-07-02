import bitcoinrpc

# JSON-RPC server user, password.  Uses HTTP Basic authentication.
rpcuser="user"
rpcpass="passwd"

connection = bitcoinrpc.connect_to_remote(rpcuser, rpcpass, host='localhost', port=9333, use_https=False)
address = connection.getnewaddress()
print address
