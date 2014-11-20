from reversecoin import bitcoinrpc

# JSON-RPC server user, password.  Uses HTTP Basic authentication.
rpcuser = "user"
rpcpass = "passwd"
address = "16UwLL9Risc3QfPqBUvKofHmBQ7wMtjvM"

connection = bitcoinrpc.connect_to_remote(rpcuser, rpcpass, host='localhost', port=9333, use_https=False)

info = connection.getinfo()

print "Blocks: %i" % info.blocks
