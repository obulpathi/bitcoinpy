#!/usr/bin/env python

import binascii
import hashlib
from bitcoin.key import CKey as Key
from bitcoin.base58 import encode, decode
from bitcoin.script import OP_DUP, OP_HASH160, OP_EQUALVERIFY, OP_CHECKSIG

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

def public_key_hex_to_pay_to_pubkey(public_key_hex):
    script = "41" + public_key_hex + "AC"
    return binascii.unhexlify(script)
        
def public_key_to_pay_to_pubkey(public_key):
    script = "41" + binascii.hexlify(public_key) + "AC"
    return binascii.unhexlify(script)

def address_to_pay_to_pubkey_hash(address):
    pubkey_hash = address_to_public_key_hash(address)
    script = "76A914" + str(binascii.hexlify(pubkey_hash)) + "88AC"
    print script
    # script = str(hex(OP_DUP)[2:]) + str(hex(OP_HASH160)[2:]) + "14" + str(binascii.hexlify(pubkey_hash)) + str(hex(OP_EQUALVERIFY)[2:]) + str(hex(OP_CHECKSIG)[2:])
    return binascii.unhexlify(script)

def sriptSig_to_pubkey(script):
    len_signed_data = ord(script[0])
    len_pubkey_data = ord(script[len_signed_data:len_signed_data+1])
    return script[-len_pubkey_data:]
    
def output_script_to_public_key_hash(script):
    # better matching .. but for now . .. this should work
    if not script:
        return
    # is the script is a standard generation address
    if binascii.hexlify(script[:1]) == "41":
        return binascii.hexlify(myhash160(bytearray.fromhex(binascii.hexlify(script[1:-1]))))
    # is the script is a standard transaction address
    elif binascii.hexlify(script[:3]) == "76a914":
        return binascii.hexlify(script[3:-2])
    else:
        pass
        #print "Error scritpt: ", binascii.hexlify(script)
    return None

def scriptSig_to_public_key_hash(script):
    if not script:
        return
    # remove the signature
    signature_length = ord(script[:1])
    script = script[1 + signature_length:]
    # remove pubkey length and return
    return script [1:]
    
"""
# Output script to address representation
def script_to_address(script,vbyte=0):
    if re.match('^[0-9a-fA-F]*$',script):
        script = script.decode('hex')
    if script[:3] == '\x76\xa9\x14' and script[-2:] == '\x88\xac' and len(script) == 25:
        return bin_to_b58check(script[3:-2],vbyte) # pubkey hash addresses
    else:
        return bin_to_b58check(script[2:-1],5) # BIP0016 scripthash addresses

def p2sh_scriptaddr(script):
    if re.match('^[0-9a-fA-F]*$',script): script = script.decode('hex')
    return hex_to_b58check(hash160(script),5)
"""

### Scripts
def mk_pubkey_script(addr): # Keep the auxiliary functions around for altcoins' sake
    return '76a914' + b58check_to_hex(addr) + '88ac'

def mk_scripthash_script(addr):
    return 'a914' + b58check_to_hex(addr) + '87'

# Address representation to output script
def address_to_script(addr):
    if addr[0] == '3': return mk_scripthash_script(addr)
    else: return mk_pubkey_script(addr)
    
def address_to_output_script(address):
    pass

# FIX ME: fees is not fixed, but for now its isset to 1
def calculate_fees(tx):
    return 1
    
if __name__ == "__main__":
    address1 = "16UwLL9Risc3QfPqBUvKofHmBQ7wMtjvM"
    address2 = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
    public_key_hex1 = "0450863AD64A87AE8A2FE83C1AF1A8403CB53F53E486D8511DAD8A04887E5B23522CD470243453A299FA9E77237716103ABC11A1DF38855ED6F2EE187E9C582BA6"
    public_key_hex2 = "04678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5f"
    # print "address: ", address1
    # print "public key_hex: ", public_key_hex1
    #print "public_keys_hex: ", public_key_hex1, public_key_hex2
    # print "public key to address: ", public_key_hex_to_address(public_key_hex1)
    # print "address to public key hash: ", binascii.hexlify(address_to_public_key_hash(address1))
    # print "public key hash: ", binascii.hexlify(myhash160(bytearray.fromhex(public_key_hex1)))
    address = '1AqTMY7kmHZxBuLUR5wJjPFUvqGs23sesr'
    print binascii.hexlify(address_to_pay_to_pubkey_hash(address))
