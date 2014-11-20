import bitcoinrpc
from bitcoinrpc.exceptions import InsufficientFunds

conn = bitcoinrpc.connect_to_local()
try:
    conn.move("testaccount", "testaccount2", 1.0)
except InsufficientFunds,e:
    print "Account does not have enough funds available!"
info = conn.getinfo()
print "Blocks: %i" % info.blocks
print "Connections: %i" % info.connections
print "Difficulty: %f" % info.difficulty

conn.sendtoaddress("msTGAm1ApjEJfsWfAaRVaZHRm26mv5GL73", 20.0)
pay_to = conn.getnewaddress()
print "We will ship the pirate sandwidth after payment of 200 coins to ", pay_to
amount = conn.getreceivedbyaddress(pay_to)
if amount > 200.0:
        print "Thanks, your sandwitch will be prepared and shipped."
