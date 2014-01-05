import bitcoinrpc

# JSON-RPC server user, password.  Uses HTTP Basic authentication.
rpcuser="mango"
rpcpass="DSUEONJSdhsjdscqowdilkfe8re878e78fhdo483fcn8"

connection = bitcoinrpc.connect_to_remote(rpcuser, rpcpass, host='localhost', port=9333, use_https=False)

address = connection.getnewaddress()
print "New address: ", address
