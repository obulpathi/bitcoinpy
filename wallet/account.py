import bitcoinrpc

# JSON-RPC server user, password.  Uses HTTP Basic authentication.
rpcuser = "user"
rpcpass = "passwd"
account = "account"

connection = bitcoinrpc.connect_to_remote(rpcuser, rpcpass, host='localhost', port=9333, use_https=False)
addressmap = connection.getaccount(account)
for account in addressmap:
    print account['address'], account['public_key'], account['private_key'], account['balance']
