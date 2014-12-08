#!/usr/bin/env python

import binascii
from bitcoin.core import COutPoint, CTxIn, CTxOut, CTransaction, CBlock



coinbase = "04ffff001d0104455468652054696d65732030332f4a616e2f32303039204368616e63656c6c6f72206f6e206272696e6b206f66207365636f6e64206261696c6f757420666f722062616e6b73"
scriptPubKeyHex = "4104678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5fac"

# construct previous out point
previousOut = COutPoint()
previousOut.hash = 0
previousOut.n = 4294967295

# construct txin
txin = CTxIn()
txin.coinbase = binascii.unhexlify(coinbase)
txin.scriptSig = binascii.unhexlify(coinbase)
txin.prevout = previousOut

# construct txout
txout = CTxOut()
txout.nValue = 5000000000
txout.scriptPubKey = binascii.unhexlify(scriptPubKeyHex)

# create transaction
tx = CTransaction()
tx.vin.append(txin)
tx.vout.append(txout)
tx.calc_sha256()
print tx
print "Transaction: ", tx.is_valid()
print "hash: ", hex(tx.sha256)
print "Hash: ", "0x4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b"

block = CBlock()
block.nVersion = 1
block.hashPrevBlock = 0
block.hashMerkleRoot = 0x4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b
block.nTime    = 1231006505
block.nBits    = 486604799 # 0x1d00ffff
block.nNonce   = 2083236893
block.vtx = [tx]

block.calc_sha256()
print "Calculated hash: ", hex(block.sha256)
print " >>>>>>>>>>>>>>: ", "0x000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f"
#
#print block.is_valid()

genesis = binascii.hexlify(block.serialize())
print "Version: ", genesis[:8]
print "Previous block: ", genesis[8:72]
print "Merkle root: ", genesis[72:136]
print "Match      : ", "3BA3EDFD7A7B12B27AC72C3E67768F617FC81BC3888A51323A9FB8AA4B1E5E4A"
print "Time stamp: ", genesis[136:144]
print "Match:    : ", "29AB5F49"
print "nBits: ", genesis[144:152]
print "Match: ", "FFFF001D"
print "Nonce: ", genesis[152:160]
print "Match: ", "1DAC2B7C"
print "# transactions: ", genesis[160:162]
print "Match         : ", "01"
print "Version: ", genesis[162:170]
print "Input: ", genesis[170:172]
print "previous out:", genesis[172:244]
print "Match       :", "0000000000000000000000000000000000000000000000000000000000000000FFFFFFFF"
print "Script length: ", genesis[244:246]
print "scriptSig: ", genesis[246:400]
print "match    : ", "04FFFF001D0104455468652054696D65732030332F4A616E2F32303039204368616E63656C6C6F72206F6E206272696E6B206F66207365636F6E64206261696C6F757420666F722062616E6B73"
print "sequence: ", genesis[400:408]
print "match   : ", "ffffffff"
print "outputs: ", genesis[408:410]
print "nValue:", genesis[410:426]
print "match: ", "00F2052A01000000"
print "script length: ", genesis[426:428]
print "out put script: ", genesis[428:562]
print "match:          ", "4104678AFDB0FE5548271967F1A67130B7105CD6A828E03909A67962E0EA1F61DEB649F6BC3F4CEF38C4F35504E51EC112DE5C384DF7BA0B8D578A4C702B6BF11D5FAC"
print "lock time : ", genesis[562:570]

blkchain = open('genesis.dat', 'wb')
magic = "bef9d9b4011d0000"
magic = 'f9beb4d91d010000'
blkchain.write(binascii.unhexlify(magic + genesis))
blkchain.close()

"""
4D - script length
04FFFF001D0104455468652054696D65732030332F4A616E2F32303039204368616E63656C6C6F72206F6E206272696E6B206F66207365636F6E64206261696C6F757420666F722062616E6B73 - scriptsig
FFFFFFFF - sequence
01 - outputs
00F2052A01000000 - 50 BTC
43 - pk_script length
4104678AFDB0FE5548271967F1A67130B7105CD6A828E03909A67962E0EA1F61DEB649F6BC3F4CEF38C4F35504E51EC112DE5C384DF7BA0B8D578A4C702B6BF11D5FAC - pk_script
00000000 - lock time
"""

"""
{
  "hash":"000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f",
  "ver":1,
  "prev_block":"0000000000000000000000000000000000000000000000000000000000000000",
  "mrkl_root":"4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b",
  "time":1231006505,
  "bits":486604799,
  "nonce":2083236893,
  "n_tx":1,
  "size":285,
  "tx":[
    {
      "hash":"4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b",
      "ver":1,
      "vin_sz":1,
      "vout_sz":1,
      "lock_time":0,
      "size":204,
      "in":[
        {
          "prev_out":{
            "hash":"0000000000000000000000000000000000000000000000000000000000000000",
            "n":4294967295
          },
          "coinbase":"04ffff001d0104455468652054696d65732030332f4a616e2f32303039204368616e63656c6c6f72206f6e206272696e6b206f66207365636f6e64206261696c6f757420666f722062616e6b73"
        }
      ],
      "out":[
        {
          "value":"50.00000000",
          "scriptPubKey":"04678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5f OP_CHECKSIG"
        }
      ]
    }
  ],
  "mrkl_tree":[
    "4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b"
  ]
}
"""
