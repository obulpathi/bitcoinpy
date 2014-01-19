import hashlib
import binascii
from bitcoin.key import CKey as Key
from bitcoin.base58 import encode, decode

# bitcoin addresses testing: http://gobittest.appspot.com/
# validate: https://en.bitcoin.it/wiki/Technical_background_of_Bitcoin_addresses

def MyHash(s):
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()

def MyHash160(s):
    h = hashlib.new('ripemd160')
    h.update(hashlib.sha256(s).digest())
    return h.digest()
    
# Generate public and private keys
key = Key()
# key.set_privkey(0x18E14A7B6A307F426A94F8114701E7C8E774E7F9A47E2C2035DB29A206321725)
# key.set_pubkey(bytearray.fromhex("0450863AD64A87AE8A2FE83C1AF1A8403CB53F53E486D8511DAD8A04887E5B23522CD470243453A299FA9E77237716103ABC11A1DF38855ED6F2EE187E9C582BA6"))
key.generate()
key.set_compressed(True)
private_key = key.get_privkey()
public_key = key.get_pubkey()
secret = key.get_secret()
private_key_hex = private_key.encode('hex')
public_key_hex = public_key.encode('hex')
secret_hex = binascii.hexlify(secret)
print "Private key: ", private_key_hex
print "Public key: ", public_key_hex
print "secret    : ", secret_hex

public_key = bytearray.fromhex(public_key_hex)
# public_key = bytearray.fromhex("0450863AD64A87AE8A2FE83C1AF1A8403CB53F53E486D8511DAD8A04887E5B23522CD470243453A299FA9E77237716103ABC11A1DF38855ED6F2EE187E9C582BA6")

# Perform SHA-256 and RIPEMD-160 hashing on public key
hash160_address = MyHash160(public_key)

# add version byte: 0x00 for Main Network
extended_address = '\x00' + hash160_address

# generate double SHA-256 hash of extended address
hash_address = MyHash(extended_address)

# Take the first 4 bytes of the second SHA-256 hash. This is the address checksum
checksum = hash_address[:4]

# Add the 4 checksum bytes from point 7 at the end of extended RIPEMD-160 hash from point 4. This is the 25-byte binary Bitcoin Address.
binary_address = extended_address + checksum

# Convert the result from a byte string into a base58 string using Base58Check encoding.
address = encode(binary_address)
print address


"""
How to create Bitcoin Address

0 - Having a private ECDSA key

   18E14A7B6A307F426A94F8114701E7C8E774E7F9A47E2C2035DB29A206321725
1 - Take the corresponding public key generated with it (65 bytes, 1 byte 0x04, 32 bytes corresponding to X coordinate, 32 bytes corresponding to Y coordinate)

   0450863AD64A87AE8A2FE83C1AF1A8403CB53F53E486D8511DAD8A04887E5B23522CD470243453A299FA9E77237716103ABC11A1DF38855ED6F2EE187E9C582BA6
2 - Perform SHA-256 hashing on the public key

   600FFE422B4E00731A59557A5CCA46CC183944191006324A447BDB2D98D4B408
3 - Perform RIPEMD-160 hashing on the result of SHA-256

   010966776006953D5567439E5E39F86A0D273BEE
4 - Add version byte in front of RIPEMD-160 hash (0x00 for Main Network)

   00010966776006953D5567439E5E39F86A0D273BEE
5 - Perform SHA-256 hash on the extended RIPEMD-160 result

   445C7A8007A93D8733188288BB320A8FE2DEBD2AE1B47F0F50BC10BAE845C094
6 - Perform SHA-256 hash on the result of the previous SHA-256 hash

   D61967F63C7DD183914A4AE452C9F6AD5D462CE3D277798075B107615C1A8A30
7 - Take the first 4 bytes of the second SHA-256 hash. This is the address checksum

   D61967F6
8 - Add the 4 checksum bytes from point 7 at the end of extended RIPEMD-160 hash from point 4. This is the 25-byte binary Bitcoin Address.

   00010966776006953D5567439E5E39F86A0D273BEED61967F6
9 - Convert the result from a byte string into a base58 string using Base58Check encoding. This is the most commonly used Bitcoin Address format

   16UwLL9Risc3QfPqBUvKofHmBQ7wMtjvM
"""
