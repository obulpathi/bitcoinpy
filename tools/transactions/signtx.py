import binascii
import hashlib

from bitcoin.key import CKey

from bitcoin.core import COutPoint, CTxIn, CTxOut, CTransaction

# from utils
def myhash(s):
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()

previous = COutPoint()
txin = CTxIn()
txout = CTxOut()
tx = CTransaction()

# get the outpoint from which we want to spend
previous.hash = 0xeccf7e3034189b851985d871f91384b8ee357cd47c3024736e5676eb2debb3f2
previous.n = 0x01000000
txin.prevout = previous
txin.scriptSig = binascii.unhexlify("76a914010966776006953d5567439e5e39f86a0d273bee88ac")

# create output transaction
txout.nValue = 0x605af40500000000
txout.scriptPubKey = binascii.unhexlify("76a914097072524438d003d23a2f23edb65aae1bb3e46988ac")

# set inputs and outputs
tx.vin.append(txin)
tx.vout.append(txout)
sertx = tx.serialize() + binascii.unhexlify("01000000")

"""
print sertx[:76]
print sertx[76:152]
print sertx[152:]
"""

dhash = myhash(sertx)
print binascii.hexlify(dhash)
print "9302bda273a887cb40c13e02a50b4071a31fd3aae3ae04021b0b843dd61ad18e"

# sign the transaction now

print "\n\n"
x = """
0100000001eccf7e3034189b851985d871f91384b8ee357cd47c3024736e5676eb2debb3f201
0000001976a914010966776006953d5567439e5e39f86a0d273bee88acffffffff01605af405
000000001976a914097072524438d003d23a2f23edb65aae1bb3e46988ac0000000001000000"""
# print x
dhash = binascii.unhexlify("9302bda273a887cb40c13e02a50b4071a31fd3aae3ae04021b0b843dd61ad18e")

PRIVATE_KEY=0x18E14A7B6A307F426A94F8114701E7C8E774E7F9A47E2C2035DB29A206321725
HEX_TRANSACTION="010000000126c07ece0bce7cda0ccd14d99e205f118cde27e83dd75da7b141fe487b5528fb000000008b48304502202b7e37831273d74c8b5b1956c23e79acd660635a8d1063d413c50b218eb6bc8a022100a10a3a7b5aaa0f07827207daf81f718f51eeac96695cf1ef9f2020f21a0de02f01410452684bce6797a0a50d028e9632be0c2a7e5031b710972c2a3285520fb29fcd4ecfb5fc2bf86a1e7578e4f8a305eeb341d1c6fc0173e5837e2d3c7b178aade078ffffffff02b06c191e010000001976a9143564a74f9ddb4372301c49154605573d7d1a88fe88ac00e1f505000000001976a914010966776006953d5567439e5e39f86a0d273bee88ac00000000"
#output to redeem. must exist in HEX_TRANSACTION

k = CKey()
k.generate(('%064x' % PRIVATE_KEY).decode('hex'))

#here we retrieve the public key data generated from the supplied private key
pubkey_data = k.get_pubkey()
#then we create a signature over the hash of the signature-less transaction
signed_data = k.sign(dhash)
print binascii.hexlify(signed_data)

"""
# Add four-byte version field: 01000000
# One-byte varint specifying the number of inputs: 01
# 32-byte hash of the transaction from which we want to redeem an output: eccf7e3034189b851985d871f91384b8ee357cd47c3024736e5676eb2debb3f2
# Four-byte field denoting the output index we want to redeem from the transaction with the above hash (output number 2 = output index 1): 01000000
Now comes the scriptSig. For the purpose of signing the transaction, this is temporarily filled with the scriptPubKey of the output we want to redeem. First we write a one-byte varint which denotes the length of the scriptSig (0x19 = 25 bytes): 19
Then we write the actual scriptSig (which is the scriptPubKey of the output we want to redeem): 76a914010966776006953d5567439e5e39f86a0d273bee88ac
Then we write a four-byte field denoting the sequence. This is currently always set to 0xffffffff: ffffffff
# Next comes a one-byte varint containing the number of outputs in our new transaction. We will set this to 1 in this example: 01       
# We then write an 8-byte field (64 bit integer) containing the amount we want to redeem from the specified output. I will set this to the total amount available 
#   in the   output minus a fee of 0.001 BTC (0.999 BTC, or 99900000 Satoshis): 605af40500000000
# Then we start writing our transaction's output. We start with a one-byte varint denoting the length of the output script (0x19 or 25 bytes): 19
# Then the actual output script: 76a914097072524438d003d23a2f23edb65aae1bb3e46988ac
# Then we write the four-byte "lock time" field: 00000000
And at last, we write a four-byte "hash code type" (1 in our case): 01000000
"""
