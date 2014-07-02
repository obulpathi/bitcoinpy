#!/usr/bin/env python

import hashlib
from bitcoin.key import CKey

b58_digits = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def dhash(s):
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()
    
def rhash(s):
    h1 = hashlib.new('ripemd160')
    h1.update(hashlib.sha256(s).digest())
    return h1.digest()

def base58_check_encode(s, version=0):
    vs = chr(version) + s
    check = dhash(vs)[:4]
    return base58_encode_padded(vs + check)

def base58_encode_padded(s):
    res = base58_encode(int('0x' + s.encode('hex'), 16))
    pad = 0
    for c in s:
        if c == chr(0):
            pad += 1
        else:
            break
    return b58_digits[0] * pad + res

def base58_encode(n):
    l = []
    while n > 0:
        n, r = divmod(n, 58)
        l.insert(0,(b58_digits[r]))
    return ''.join(l)
    
def generate_address():
# def get_addr(k,version = 0):
    k = CKey()
    version = 0
    k.generate()
    k.set_compressed(True)
    pubkey = k.get_pubkey()
    secret = k.get_secret()
    hash160 = rhash(pubkey)
    addr = base58_check_encode(hash160, version)
    # payload = secret
    # if k.compressed:
    #    payload = secret + chr(1)
    pkey = base58_check_encode(payload, 128+version)
    return addr, pkey

if __name__ == "__main__":
    address, private_key = generate_address()
    print "Address: ", address
    print "Private key:", private_key
