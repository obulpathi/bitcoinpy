#!/usr/bin/env python

import binascii
import hashlib
from bitcoin.key import CKey as Key
from bitcoin.base58 import encode, decode

def myhash(s):
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()

def myhash160(s):
    h = hashlib.new('ripemd160')
    h.update(hashlib.sha256(s).digest())
    return h.digest()

def getnewaddress():
    # Generate public and private keys
    key = Key()
    key.generate()
    key.set_compressed(True)
    private_key = key.get_privkey()
    public_key = key.get_pubkey()
    private_key_hex = private_key.encode('hex')
    public_key_hex = public_key.encode('hex')
    public_key_bytearray = bytearray.fromhex(public_key_hex)
    # Perform SHA-256 and RIPEMD-160 hashing on public key
    hash160_address = myhash160(public_key_bytearray)
    # add version byte: 0x00 for Main Network
    extended_address = '\x00' + hash160_address
    # generate double SHA-256 hash of extended address
    hash_address = myhash(extended_address)
    # Take the first 4 bytes of the second SHA-256 hash. This is the address checksum
    checksum = hash_address[:4]
    # Add the 4 checksum bytes from point 7 at the end of extended RIPEMD-160 hash from point 4. This is the 25-byte binary Bitcoin Address.
    binary_address = extended_address + checksum
    # Convert the result from a byte string into a base58 string using Base58Check encoding.
    address = encode(binary_address)
    return public_key, private_key, address

def public_key_to_address(public_key):
    public_key_hex = public_key.encode('hex')
    public_key_bytearray = bytearray.fromhex(public_key_hex)
    # Perform SHA-256 and RIPEMD-160 hashing on public key
    hash160_address = myhash160(public_key_bytearray)
    # add version byte: 0x00 for Main Network
    extended_address = '\x00' + hash160_address
    # generate double SHA-256 hash of extended address
    hash_address = myhash(extended_address)
    # Take the first 4 bytes of the second SHA-256 hash. This is the address checksum
    checksum = hash_address[:4]
    # Add the 4 checksum bytes from point 7 at the end of extended RIPEMD-160 hash from point 4. This is the 25-byte binary Bitcoin Address.
    binary_address = extended_address + checksum
    address = encode(binary_address)
    return address

def public_key_hex_to_address(public_key_hex):
    public_key_bytearray = bytearray.fromhex(public_key_hex)
    # Perform SHA-256 and RIPEMD-160 hashing on public key
    hash160_address = myhash160(public_key_bytearray)
    # add version byte: 0x00 for Main Network
    extended_address = '\x00' + hash160_address
    # generate double SHA-256 hash of extended address
    hash_address = myhash(extended_address)
    # Take the first 4 bytes of the second SHA-256 hash. This is the address checksum
    checksum = hash_address[:4]
    # Add the 4 checksum bytes from point 7 at the end of extended RIPEMD-160 hash from point 4. This is the 25-byte binary Bitcoin Address.
    binary_address = extended_address + checksum
    address = encode(binary_address)
    return address

# fix this
def address_to_public_key_hash(address):
    binary_address = decode(address)
    # remove the 4 checksum bytes
    extended_address = binary_address[:-4]
    # remove version byte: 0x00 for Main Network
    hash160_address = extended_address[1:]
    return hash160_address

def public_key_hex_to_pay_to_script_hash(public_key_hex):
    script = "41" + public_key_hex + "AC"
    return binascii.unhexlify(script)
    
def address_to_pay_to_pubkey_hash(address):
    print "Not implemented >>>>>>>>>>>>>>>>>>>"
    exit(0)

def output_script_to_public_key_hash(script):
    script_key_hash = binascii.hexlify(myhash160(bytearray.fromhex(binascii.hexlify(script[1:-1]))))
    return script_key_hash


def address_to_output_script(address):
    pass

if __name__ == "__main__":
    address1 = "16UwLL9Risc3QfPqBUvKofHmBQ7wMtjvM"
    address2 = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
    public_key_hex1 = "0450863AD64A87AE8A2FE83C1AF1A8403CB53F53E486D8511DAD8A04887E5B23522CD470243453A299FA9E77237716103ABC11A1DF38855ED6F2EE187E9C582BA6"
    public_key_hex2 = "04678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5f"
    print "address: ", address1
    print "public key_hex: ", public_key_hex1
    #print "public_keys_hex: ", public_key_hex1, public_key_hex2
    print "public key to address: ", public_key_hex_to_address(public_key_hex1)
    print "address to public key hash: ", binascii.hexlify(address_to_public_key_hash(address1))
    # print "public key hash: ", binascii.hexlify(myhash160(bytearray.fromhex(public_key_hex1)))
