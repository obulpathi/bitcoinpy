import bitcoinrpc
from bitcoinrpc.exceptions import InsufficientFunds

conn = bitcoinrpc.connect_to_local()
address = "bitcoin address"
amount = 1.00
conn.sendtoaddress(address, amount)
print "Paid", amount, " to ", address
