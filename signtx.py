#bitcointools
from deserialize import parse_Transaction, opcodes
from BCDataStream import BCDataStream
from base58 import bc_address_to_hash_160, b58decode, public_key_to_bc_address, hash_160_to_bc_address

import ecdsa_ssl

import Crypto.Hash.SHA256 as sha256
import Crypto.Random

#transaction, from which we want to redeem an output
HEX_TRANSACTION="010000000126c07ece0bce7cda0ccd14d99e205f118cde27e83dd75da7b141fe487b5528fb000000008b48304502202b7e37831273d74c8b5b1956c23e79acd660635a8d1063d413c50b218eb6bc8a022100a10a3a7b5aaa0f07827207daf81f718f51eeac96695cf1ef9f2020f21a0de02f01410452684bce6797a0a50d028e9632be0c2a7e5031b710972c2a3285520fb29fcd4ecfb5fc2bf86a1e7578e4f8a305eeb341d1c6fc0173e5837e2d3c7b178aade078ffffffff02b06c191e010000001976a9143564a74f9ddb4372301c49154605573d7d1a88fe88ac00e1f505000000001976a914010966776006953d5567439e5e39f86a0d273bee88ac00000000"
#output to redeem. must exist in HEX_TRANSACTION
OUTPUT_INDEX=1
#address we want to send the redeemed coins to
SEND_TO_ADDRESS="1runeksijzfVxyrpiyCY2LCBvYsSiFsCm"
#fee we want to pay (in BTC)
TX_FEE=0.001
#constant that defines the number of Satoshis per BTC
COIN=100000000
#constant used to determine which part of the transaction is hashed.
SIGHASH_ALL=1
#private key whose public key hashes to the hash contained in scriptPubKey of output number *OUTPUT_INDEX* in the transaction described in HEX_TRANSACTION
PRIVATE_KEY=0x18E14A7B6A307F426A94F8114701E7C8E774E7F9A47E2C2035DB29A206321725

def dsha256(data):
   return sha256.new(sha256.new(data).digest()).digest()

tx_data=HEX_TRANSACTION.decode('hex_codec')
tx_hash=dsha256(tx_data)

#here we use bitcointools to parse a transaction. this gives easy access to the various fields of the transaction from which we want to redeem an output
stream = BCDataStream()
stream.write(tx_data)
tx_info = parse_Transaction(stream)

if len(tx_info['txOut']) < (OUTPUT_INDEX+1):
   raise RuntimeError, "there are only %d output(s) in the transaction you're trying to redeem from. you want to redeem output index %d" % (len(tx_info['txOut']), OUTPUT_INDEX)

#this dictionary is used to store the values of the various transaction fields
#  this is useful because we need to construct one transaction to hash and sign
#  and another that will be the final transaction
tx_fields = {}

##here we start creating the transaction that we hash and sign
sign_tx = BCDataStream()
##first we write the version number, which is 1
tx_fields['version'] = 1
sign_tx.write_int32(tx_fields['version'])
##then we write the number of transaction inputs, which is one
tx_fields['num_txin'] = 1
sign_tx.write_compact_size(tx_fields['num_txin'])

##then we write the actual transaction data
#'prevout_hash'
tx_fields['prevout_hash'] = tx_hash
sign_tx.write(tx_fields['prevout_hash']) #hash of the the transaction from which we want to redeem an output
#'prevout_n'
tx_fields['output_index'] = OUTPUT_INDEX
sign_tx.write_uint32(tx_fields['output_index']) #which output of the transaction with tx id 'prevout_hash' do we want to redeem?

##next comes the part of the transaction input. here we place the script of the *output* that we want to redeem
tx_fields['scriptSigHash'] = tx_info['txOut'][OUTPUT_INDEX]['scriptPubKey']
#first write the size
sign_tx.write_compact_size(len(tx_fields['scriptSigHash']))
#then the data
sign_tx.write(tx_fields['scriptSigHash'])

#'sequence'
tx_fields['sequence'] = 0xffffffff
sign_tx.write_uint32(tx_fields['sequence'])

##then we write the number of transaction outputs. we'll just use a single output in this example
tx_fields['num_txout'] = 1
sign_tx.write_compact_size(tx_fields['num_txout'])
##then we write the actual transaction output data
#we'll redeem everything from the original output minus TX_FEE
tx_fields['value'] = tx_info['txOut'][OUTPUT_INDEX]['value']-(TX_FEE*COIN)
sign_tx.write_int64(tx_fields['value'])
##this is where our scriptPubKey goes (a script that pays out to an address)
#we want the following script:
#"OP_DUP OP_HASH160  OP_EQUALVERIFY OP_CHECKSIG"
address_hash = bc_address_to_hash_160(SEND_TO_ADDRESS)
#chr(20) is the length of the address_hash (20 bytes or 160 bits)
scriptPubKey = chr(opcodes.OP_DUP) + chr(opcodes.OP_HASH160) + \
   chr(20) + address_hash + chr(opcodes.OP_EQUALVERIFY) + chr(opcodes.OP_CHECKSIG)
#first write the length of this lump of data
tx_fields['scriptPubKey'] = scriptPubKey
sign_tx.write_compact_size(len(tx_fields['scriptPubKey']))
#then the data
sign_tx.write(tx_fields['scriptPubKey'])

#write locktime (0)
tx_fields['locktime'] = 0
sign_tx.write_uint32(tx_fields['locktime'])
#and hash code type (1)
tx_fields['hash_type'] = SIGHASH_ALL
sign_tx.write_int32(tx_fields['hash_type'])

#then we obtain the hash of the signature-less transaction (the hash that we sign using our private key)
hash_scriptless = dsha256(sign_tx.input)

##now we begin with the ECDSA stuff.
## we create a private key from the provided private key data, and sign hash_scriptless with it
## we also check that the private key's corresponding public key can actually redeem the specified output

k = ecdsa_ssl.KEY()
k.generate(('%064x' % PRIVATE_KEY).decode('hex'))

#here we retrieve the public key data generated from the supplied private key
pubkey_data = k.get_pubkey()
#then we create a signature over the hash of the signature-less transaction
sig_data=k.sign(hash_scriptless)
#a one byte "hash type" is appended to the end of the signature (https://en.bitcoin.it/wiki/OP_CHECKSIG)
sig_data = sig_data + chr(SIGHASH_ALL)

#let's check that the provided privat key can actually redeem the output in question
if (bc_address_to_hash_160(public_key_to_bc_address(pubkey_data)) != tx_info['txOut'][OUTPUT_INDEX]['scriptPubKey'][3:-2]):
   bytes = b58decode(SEND_TO_ADDRESS, 25)
   raise RuntimeError, "The supplied private key cannot be used to redeem output index %d\nYou need to supply the private key for address %s" % \
                           (OUTPUT_INDEX, hash_160_to_bc_address(tx_info['txOut'][OUTPUT_INDEX]['scriptPubKey'][3:-2], bytes[0]))

##now we begin creating the final transaction. this is a duplicate of the signature-less transaction,
## with the scriptSig filled out with a script that pushes the signature plus one-byte hash code type, and public key from above, to the stack

final_tx = BCDataStream()
final_tx.write_int32(tx_fields['version'])
final_tx.write_compact_size(tx_fields['num_txin'])
final_tx.write(tx_fields['prevout_hash'])
final_tx.write_uint32(tx_fields['output_index'])

##now we need to write the actual scriptSig.
## this consists of the DER-encoded values r and s from the signature, a one-byte hash code type, and the public key in uncompressed format
## we also need to prepend the length of these two data pieces (encoded as a single byte
## containing the length), before each data piece. this length is a script opcode that tells the
## Bitcoin script interpreter to push the x following bytes onto the stack

scriptSig = chr(len(sig_data)) + sig_data + chr(len(pubkey_data)) + pubkey_data
#first write the length of this data
final_tx.write_compact_size(len(scriptSig))
#then the data
final_tx.write(scriptSig)

##and then we simply write the same data after the scriptSig that is in the signature-less transaction,
#  leaving out the four-byte hash code type (as this is encoded in the single byte following the signature data)

final_tx.write_uint32(tx_fields['sequence'])
final_tx.write_compact_size(tx_fields['num_txout'])
final_tx.write_int64(tx_fields['value'])
final_tx.write_compact_size(len(tx_fields['scriptPubKey']))
final_tx.write(tx_fields['scriptPubKey'])
final_tx.write_uint32(tx_fields['locktime'])

#prints out the final transaction in hex format (can be used as an argument to bitcoind's sendrawtransaction)
print final_tx.input.encode('hex')
