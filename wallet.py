#!/usr/bin/env python

import os
import os.path
from bsddb.db import *

"""
#-*- coding: utf-8 -*-
pywversion="2.1.7"
never_update=False

#
# jackjack's pywallet.py
# https://github.com/jackjack-jj/pywallet
# forked from Joric's pywallet.py
#




beta_version =  ('a' in pywversion.split('-')[0]) or ('b' in pywversion.split('-')[0])

missing_dep = []

try:
	from bsddb.db import *
except:
	missing_dep.append('bsddb')

import os, sys, time, re
pyw_filename = os.path.basename(__file__)
pyw_path = os.path.dirname(os.path.realpath(__file__))

try:
	for i in os.listdir('/usr/lib/python2.5/site-packages'):
		if 'Twisted' in i:
			sys.path.append('/usr/lib/python2.5/site-packages/'+i)
except:
	''

import logging
import struct
import StringIO
import traceback
import socket
import types
import string
import exceptions
import hashlib
import random
import urllib
import math

try:
	from twisted.internet import reactor
	from twisted.web import server, resource
	from twisted.web.static import File
	from twisted.python import log
except:
	missing_dep.append('twisted')

from datetime import datetime
from subprocess import *

import platform

max_version = 81000
addrtype = 0
json_db = {}
private_keys = []
private_hex_keys = []
passphrase = ""
global_merging_message = ["",""]

balance_site = 'http://jackjack.alwaysdata.net/balance/index.php?address'
aversions = {};
for i in range(256):
	aversions[i] = "version %d" % i;
aversions[0] = 'Bitcoin';
aversions[48] = 'Litecoin';
aversions[52] = 'Namecoin';
aversions[111] = 'Testnet';

wallet_dir = ""
wallet_name = ""
wallet_db = None

ko = 1e3
kio = 1024
Mo = 1e6
Mio = 1024 ** 2
Go = 1e9
Gio = 1024 ** 3
To = 1e12
Tio = 1024 ** 4

prekeys = ["308201130201010420".decode('hex'), "308201120201010420".decode('hex')]
postkeys = ["a081a530".decode('hex'), "81a530".decode('hex')]

def iais(a):
	if a>= 2:
		return 's'
	else:
		return ''

def systype():
	if platform.system() == "Darwin":
		return 'Mac'
	elif platform.system() == "Windows":
		return 'Win'
	return 'Linux'

def determine_db_dir():
	if wallet_dir in "":
		if platform.system() == "Darwin":
			return os.path.expanduser("~/Library/Application Support/Bitcoin/")
		elif platform.system() == "Windows":
			return os.path.join(os.environ['APPDATA'], "Bitcoin")
		return os.path.expanduser("~/.bitcoin")
	else:
		return wallet_dir

def determine_db_name():
	if wallet_name in "":
		return "wallet.dat"
	else:
		return wallet_name

########################
# begin of aes.py code #
########################

# from the SlowAES project, http://code.google.com/p/slowaes (aes.py)

def append_PKCS7_padding(s):
	"return s padded to a multiple of 16-bytes by PKCS7 padding"
	numpads = 16 - (len(s)%16)
	return s + numpads*chr(numpads)

def strip_PKCS7_padding(s):
	"return s stripped of PKCS7 padding"
	if len(s)%16 or not s:
		raise ValueError("String of len %d can't be PCKS7-padded" % len(s))
	numpads = ord(s[-1])
	if numpads > 16:
		raise ValueError("String ending with %r can't be PCKS7-padded" % s[-1])
	return s[:-numpads]

class AES(object):
	# valid key sizes
	keySize = dict(SIZE_128=16, SIZE_192=24, SIZE_256=32)

	# Rijndael S-box
	sbox =  [0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67,
			0x2b, 0xfe, 0xd7, 0xab, 0x76, 0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59,
			0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0, 0xb7,
			0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1,
			0x71, 0xd8, 0x31, 0x15, 0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05,
			0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75, 0x09, 0x83,
			0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29,
			0xe3, 0x2f, 0x84, 0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b,
			0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf, 0xd0, 0xef, 0xaa,
			0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c,
			0x9f, 0xa8, 0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc,
			0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2, 0xcd, 0x0c, 0x13, 0xec,
			0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19,
			0x73, 0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee,
			0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb, 0xe0, 0x32, 0x3a, 0x0a, 0x49,
			0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
			0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4,
			0xea, 0x65, 0x7a, 0xae, 0x08, 0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6,
			0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a, 0x70,
			0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9,
			0x86, 0xc1, 0x1d, 0x9e, 0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e,
			0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf, 0x8c, 0xa1,
			0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0,
			0x54, 0xbb, 0x16]

	# Rijndael Inverted S-box
	rsbox = [0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38, 0xbf, 0x40, 0xa3,
			0x9e, 0x81, 0xf3, 0xd7, 0xfb , 0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f,
			0xff, 0x87, 0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde, 0xe9, 0xcb , 0x54,
			0x7b, 0x94, 0x32, 0xa6, 0xc2, 0x23, 0x3d, 0xee, 0x4c, 0x95, 0x0b,
			0x42, 0xfa, 0xc3, 0x4e , 0x08, 0x2e, 0xa1, 0x66, 0x28, 0xd9, 0x24,
			0xb2, 0x76, 0x5b, 0xa2, 0x49, 0x6d, 0x8b, 0xd1, 0x25 , 0x72, 0xf8,
			0xf6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xd4, 0xa4, 0x5c, 0xcc, 0x5d,
			0x65, 0xb6, 0x92 , 0x6c, 0x70, 0x48, 0x50, 0xfd, 0xed, 0xb9, 0xda,
			0x5e, 0x15, 0x46, 0x57, 0xa7, 0x8d, 0x9d, 0x84 , 0x90, 0xd8, 0xab,
			0x00, 0x8c, 0xbc, 0xd3, 0x0a, 0xf7, 0xe4, 0x58, 0x05, 0xb8, 0xb3,
			0x45, 0x06 , 0xd0, 0x2c, 0x1e, 0x8f, 0xca, 0x3f, 0x0f, 0x02, 0xc1,
			0xaf, 0xbd, 0x03, 0x01, 0x13, 0x8a, 0x6b , 0x3a, 0x91, 0x11, 0x41,
			0x4f, 0x67, 0xdc, 0xea, 0x97, 0xf2, 0xcf, 0xce, 0xf0, 0xb4, 0xe6,
			0x73 , 0x96, 0xac, 0x74, 0x22, 0xe7, 0xad, 0x35, 0x85, 0xe2, 0xf9,
			0x37, 0xe8, 0x1c, 0x75, 0xdf, 0x6e , 0x47, 0xf1, 0x1a, 0x71, 0x1d,
			0x29, 0xc5, 0x89, 0x6f, 0xb7, 0x62, 0x0e, 0xaa, 0x18, 0xbe, 0x1b ,
			0xfc, 0x56, 0x3e, 0x4b, 0xc6, 0xd2, 0x79, 0x20, 0x9a, 0xdb, 0xc0,
			0xfe, 0x78, 0xcd, 0x5a, 0xf4 , 0x1f, 0xdd, 0xa8, 0x33, 0x88, 0x07,
			0xc7, 0x31, 0xb1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xec, 0x5f , 0x60,
			0x51, 0x7f, 0xa9, 0x19, 0xb5, 0x4a, 0x0d, 0x2d, 0xe5, 0x7a, 0x9f,
			0x93, 0xc9, 0x9c, 0xef , 0xa0, 0xe0, 0x3b, 0x4d, 0xae, 0x2a, 0xf5,
			0xb0, 0xc8, 0xeb, 0xbb, 0x3c, 0x83, 0x53, 0x99, 0x61 , 0x17, 0x2b,
			0x04, 0x7e, 0xba, 0x77, 0xd6, 0x26, 0xe1, 0x69, 0x14, 0x63, 0x55,
			0x21, 0x0c, 0x7d]

	def getSBoxValue(self,num):
		"Retrieves a given S-Box Value"
		return self.sbox[num]

	def getSBoxInvert(self,num):
		"Retrieves a given Inverted S-Box Value"
		return self.rsbox[num]

	def rotate(self, word):
		" Rijndael's key schedule rotate operation.

		Rotate a word eight bits to the left: eg, rotate(1d2c3a4f) == 2c3a4f1d
		Word is an char list of size 4 (32 bits overall).
		"
		return word[1:] + word[:1]

	# Rijndael Rcon
	Rcon = [0x8d, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36,
			0x6c, 0xd8, 0xab, 0x4d, 0x9a, 0x2f, 0x5e, 0xbc, 0x63, 0xc6, 0x97,
			0x35, 0x6a, 0xd4, 0xb3, 0x7d, 0xfa, 0xef, 0xc5, 0x91, 0x39, 0x72,
			0xe4, 0xd3, 0xbd, 0x61, 0xc2, 0x9f, 0x25, 0x4a, 0x94, 0x33, 0x66,
			0xcc, 0x83, 0x1d, 0x3a, 0x74, 0xe8, 0xcb, 0x8d, 0x01, 0x02, 0x04,
			0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36, 0x6c, 0xd8, 0xab, 0x4d,
			0x9a, 0x2f, 0x5e, 0xbc, 0x63, 0xc6, 0x97, 0x35, 0x6a, 0xd4, 0xb3,
			0x7d, 0xfa, 0xef, 0xc5, 0x91, 0x39, 0x72, 0xe4, 0xd3, 0xbd, 0x61,
			0xc2, 0x9f, 0x25, 0x4a, 0x94, 0x33, 0x66, 0xcc, 0x83, 0x1d, 0x3a,
			0x74, 0xe8, 0xcb, 0x8d, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40,
			0x80, 0x1b, 0x36, 0x6c, 0xd8, 0xab, 0x4d, 0x9a, 0x2f, 0x5e, 0xbc,
			0x63, 0xc6, 0x97, 0x35, 0x6a, 0xd4, 0xb3, 0x7d, 0xfa, 0xef, 0xc5,
			0x91, 0x39, 0x72, 0xe4, 0xd3, 0xbd, 0x61, 0xc2, 0x9f, 0x25, 0x4a,
			0x94, 0x33, 0x66, 0xcc, 0x83, 0x1d, 0x3a, 0x74, 0xe8, 0xcb, 0x8d,
			0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36, 0x6c,
			0xd8, 0xab, 0x4d, 0x9a, 0x2f, 0x5e, 0xbc, 0x63, 0xc6, 0x97, 0x35,
			0x6a, 0xd4, 0xb3, 0x7d, 0xfa, 0xef, 0xc5, 0x91, 0x39, 0x72, 0xe4,
			0xd3, 0xbd, 0x61, 0xc2, 0x9f, 0x25, 0x4a, 0x94, 0x33, 0x66, 0xcc,
			0x83, 0x1d, 0x3a, 0x74, 0xe8, 0xcb, 0x8d, 0x01, 0x02, 0x04, 0x08,
			0x10, 0x20, 0x40, 0x80, 0x1b, 0x36, 0x6c, 0xd8, 0xab, 0x4d, 0x9a,
			0x2f, 0x5e, 0xbc, 0x63, 0xc6, 0x97, 0x35, 0x6a, 0xd4, 0xb3, 0x7d,
			0xfa, 0xef, 0xc5, 0x91, 0x39, 0x72, 0xe4, 0xd3, 0xbd, 0x61, 0xc2,
			0x9f, 0x25, 0x4a, 0x94, 0x33, 0x66, 0xcc, 0x83, 0x1d, 0x3a, 0x74,
			0xe8, 0xcb ]

	def getRconValue(self, num):
		"Retrieves a given Rcon Value"
		return self.Rcon[num]

	def core(self, word, iteration):
		"Key schedule core."
		# rotate the 32-bit word 8 bits to the left
		word = self.rotate(word)
		# apply S-Box substitution on all 4 parts of the 32-bit word
		for i in range(4):
			word[i] = self.getSBoxValue(word[i])
		# XOR the output of the rcon operation with i to the first part
		# (leftmost) only
		word[0] = word[0] ^ self.getRconValue(iteration)
		return word

	def expandKey(self, key, size, expandedKeySize):
		"Rijndael's key expansion.

		Expands an 128,192,256 key into an 176,208,240 bytes key

		expandedKey is a char list of large enough size,
		key is the non-expanded key.
		"
		# current expanded keySize, in bytes
		currentSize = 0
		rconIteration = 1
		expandedKey = [0] * expandedKeySize

		# set the 16, 24, 32 bytes of the expanded key to the input key
		for j in range(size):
			expandedKey[j] = key[j]
		currentSize += size

		while currentSize < expandedKeySize:
			# assign the previous 4 bytes to the temporary value t
			t = expandedKey[currentSize-4:currentSize]

			# every 16,24,32 bytes we apply the core schedule to t
			# and increment rconIteration afterwards
			if currentSize % size == 0:
				t = self.core(t, rconIteration)
				rconIteration += 1
			# For 256-bit keys, we add an extra sbox to the calculation
			if size == self.keySize["SIZE_256"] and ((currentSize % size) == 16):
				for l in range(4): t[l] = self.getSBoxValue(t[l])

			# We XOR t with the four-byte block 16,24,32 bytes before the new
			# expanded key.  This becomes the next four bytes in the expanded
			# key.
			for m in range(4):
				expandedKey[currentSize] = expandedKey[currentSize - size] ^ \
						t[m]
				currentSize += 1

		return expandedKey

	def addRoundKey(self, state, roundKey):
		"Adds (XORs) the round key to the state."
		for i in range(16):
			state[i] ^= roundKey[i]
		return state

	def createRoundKey(self, expandedKey, roundKeyPointer):
		"Create a round key.
		Creates a round key from the given expanded key and the
		position within the expanded key.
		"
		roundKey = [0] * 16
		for i in range(4):
			for j in range(4):
				roundKey[j*4+i] = expandedKey[roundKeyPointer + i*4 + j]
		return roundKey

	def galois_multiplication(self, a, b):
		"Galois multiplication of 8 bit characters a and b."
		p = 0
		for counter in range(8):
			if b & 1: p ^= a
			hi_bit_set = a & 0x80
			a <<= 1
			# keep a 8 bit
			a &= 0xFF
			if hi_bit_set:
				a ^= 0x1b
			b >>= 1
		return p

	#
	# substitute all the values from the state with the value in the SBox
	# using the state value as index for the SBox
	#
	def subBytes(self, state, isInv):
		if isInv: getter = self.getSBoxInvert
		else: getter = self.getSBoxValue
		for i in range(16): state[i] = getter(state[i])
		return state

	# iterate over the 4 rows and call shiftRow() with that row
	def shiftRows(self, state, isInv):
		for i in range(4):
			state = self.shiftRow(state, i*4, i, isInv)
		return state

	# each iteration shifts the row to the left by 1
	def shiftRow(self, state, statePointer, nbr, isInv):
		for i in range(nbr):
			if isInv:
				state[statePointer:statePointer+4] = \
						state[statePointer+3:statePointer+4] + \
						state[statePointer:statePointer+3]
			else:
				state[statePointer:statePointer+4] = \
						state[statePointer+1:statePointer+4] + \
						state[statePointer:statePointer+1]
		return state

	# galois multiplication of the 4x4 matrix
	def mixColumns(self, state, isInv):
		# iterate over the 4 columns
		for i in range(4):
			# construct one column by slicing over the 4 rows
			column = state[i:i+16:4]
			# apply the mixColumn on one column
			column = self.mixColumn(column, isInv)
			# put the values back into the state
			state[i:i+16:4] = column

		return state

	# galois multiplication of 1 column of the 4x4 matrix
	def mixColumn(self, column, isInv):
		if isInv: mult = [14, 9, 13, 11]
		else: mult = [2, 1, 1, 3]
		cpy = list(column)
		g = self.galois_multiplication

		column[0] = g(cpy[0], mult[0]) ^ g(cpy[3], mult[1]) ^ \
					g(cpy[2], mult[2]) ^ g(cpy[1], mult[3])
		column[1] = g(cpy[1], mult[0]) ^ g(cpy[0], mult[1]) ^ \
					g(cpy[3], mult[2]) ^ g(cpy[2], mult[3])
		column[2] = g(cpy[2], mult[0]) ^ g(cpy[1], mult[1]) ^ \
					g(cpy[0], mult[2]) ^ g(cpy[3], mult[3])
		column[3] = g(cpy[3], mult[0]) ^ g(cpy[2], mult[1]) ^ \
					g(cpy[1], mult[2]) ^ g(cpy[0], mult[3])
		return column

	# applies the 4 operations of the forward round in sequence
	def aes_round(self, state, roundKey):
		state = self.subBytes(state, False)
		state = self.shiftRows(state, False)
		state = self.mixColumns(state, False)
		state = self.addRoundKey(state, roundKey)
		return state

	# applies the 4 operations of the inverse round in sequence
	def aes_invRound(self, state, roundKey):
		state = self.shiftRows(state, True)
		state = self.subBytes(state, True)
		state = self.addRoundKey(state, roundKey)
		state = self.mixColumns(state, True)
		return state

	# Perform the initial operations, the standard round, and the final
	# operations of the forward aes, creating a round key for each round
	def aes_main(self, state, expandedKey, nbrRounds):
		state = self.addRoundKey(state, self.createRoundKey(expandedKey, 0))
		i = 1
		while i < nbrRounds:
			state = self.aes_round(state,
								   self.createRoundKey(expandedKey, 16*i))
			i += 1
		state = self.subBytes(state, False)
		state = self.shiftRows(state, False)
		state = self.addRoundKey(state,
								 self.createRoundKey(expandedKey, 16*nbrRounds))
		return state

	# Perform the initial operations, the standard round, and the final
	# operations of the inverse aes, creating a round key for each round
	def aes_invMain(self, state, expandedKey, nbrRounds):
		state = self.addRoundKey(state,
								 self.createRoundKey(expandedKey, 16*nbrRounds))
		i = nbrRounds - 1
		while i > 0:
			state = self.aes_invRound(state,
									  self.createRoundKey(expandedKey, 16*i))
			i -= 1
		state = self.shiftRows(state, True)
		state = self.subBytes(state, True)
		state = self.addRoundKey(state, self.createRoundKey(expandedKey, 0))
		return state

	def encrypt(self, iput, key, size):
		output = [0] * 16
		# the number of rounds
		nbrRounds = 0
		# the 128 bit block to encode
	# encrypts a 128 bit input block against the given key of size specified
		block = [0] * 16
		# set the number of rounds
		if size == self.keySize["SIZE_128"]: nbrRounds = 10
		elif size == self.keySize["SIZE_192"]: nbrRounds = 12
		elif size == self.keySize["SIZE_256"]: nbrRounds = 14
		else: return None

		# the expanded keySize
		expandedKeySize = 16*(nbrRounds+1)

		# Set the block values, for the block:
		# a0,0 a0,1 a0,2 a0,3
		# a1,0 a1,1 a1,2 a1,3
		# a2,0 a2,1 a2,2 a2,3
		# a3,0 a3,1 a3,2 a3,3
		# the mapping order is a0,0 a1,0 a2,0 a3,0 a0,1 a1,1 ... a2,3 a3,3
		#
		# iterate over the columns
		for i in range(4):
			# iterate over the rows
			for j in range(4):
				block[(i+(j*4))] = iput[(i*4)+j]

		# expand the key into an 176, 208, 240 bytes key
		# the expanded key
		expandedKey = self.expandKey(key, size, expandedKeySize)

		# encrypt the block using the expandedKey
		block = self.aes_main(block, expandedKey, nbrRounds)

		# unmap the block again into the output
		for k in range(4):
			# iterate over the rows
			for l in range(4):
				output[(k*4)+l] = block[(k+(l*4))]
		return output

	# decrypts a 128 bit input block against the given key of size specified
	def decrypt(self, iput, key, size):
		output = [0] * 16
		# the number of rounds
		nbrRounds = 0
		# the 128 bit block to decode
		block = [0] * 16
		# set the number of rounds
		if size == self.keySize["SIZE_128"]: nbrRounds = 10
		elif size == self.keySize["SIZE_192"]: nbrRounds = 12
		elif size == self.keySize["SIZE_256"]: nbrRounds = 14
		else: return None

		# the expanded keySize
		expandedKeySize = 16*(nbrRounds+1)

		# Set the block values, for the block:
		# a0,0 a0,1 a0,2 a0,3
		# a1,0 a1,1 a1,2 a1,3
		# a2,0 a2,1 a2,2 a2,3
		# a3,0 a3,1 a3,2 a3,3
		# the mapping order is a0,0 a1,0 a2,0 a3,0 a0,1 a1,1 ... a2,3 a3,3

		# iterate over the columns
		for i in range(4):
			# iterate over the rows
			for j in range(4):
				block[(i+(j*4))] = iput[(i*4)+j]
		# expand the key into an 176, 208, 240 bytes key
		expandedKey = self.expandKey(key, size, expandedKeySize)
		# decrypt the block using the expandedKey
		block = self.aes_invMain(block, expandedKey, nbrRounds)
		# unmap the block again into the output
		for k in range(4):
			# iterate over the rows
			for l in range(4):
				output[(k*4)+l] = block[(k+(l*4))]
		return output

class AESModeOfOperation(object):

	aes = AES()

	# structure of supported modes of operation
	modeOfOperation = dict(OFB=0, CFB=1, CBC=2)

	# converts a 16 character string into a number array
	def convertString(self, string, start, end, mode):
		if end - start > 16: end = start + 16
		if mode == self.modeOfOperation["CBC"]: ar = [0] * 16
		else: ar = []

		i = start
		j = 0
		while len(ar) < end - start:
			ar.append(0)
		while i < end:
			ar[j] = ord(string[i])
			j += 1
			i += 1
		return ar

	# Mode of Operation Encryption
	# stringIn - Input String
	# mode - mode of type modeOfOperation
	# hexKey - a hex key of the bit length size
	# size - the bit length of the key
	# hexIV - the 128 bit hex Initilization Vector
	def encrypt(self, stringIn, mode, key, size, IV):
		if len(key) % size:
			return None
		if len(IV) % 16:
			return None
		# the AES input/output
		plaintext = []
		iput = [0] * 16
		output = []
		ciphertext = [0] * 16
		# the output cipher string
		cipherOut = []
		# char firstRound
		firstRound = True
		if stringIn != None:
			for j in range(int(math.ceil(float(len(stringIn))/16))):
				start = j*16
				end = j*16+16
				if  end > len(stringIn):
					end = len(stringIn)
				plaintext = self.convertString(stringIn, start, end, mode)
				# print 'PT@%s:%s' % (j, plaintext)
				if mode == self.modeOfOperation["CFB"]:
					if firstRound:
						output = self.aes.encrypt(IV, key, size)
						firstRound = False
					else:
						output = self.aes.encrypt(iput, key, size)
					for i in range(16):
						if len(plaintext)-1 < i:
							ciphertext[i] = 0 ^ output[i]
						elif len(output)-1 < i:
							ciphertext[i] = plaintext[i] ^ 0
						elif len(plaintext)-1 < i and len(output) < i:
							ciphertext[i] = 0 ^ 0
						else:
							ciphertext[i] = plaintext[i] ^ output[i]
					for k in range(end-start):
						cipherOut.append(ciphertext[k])
					iput = ciphertext
				elif mode == self.modeOfOperation["OFB"]:
					if firstRound:
						output = self.aes.encrypt(IV, key, size)
						firstRound = False
					else:
						output = self.aes.encrypt(iput, key, size)
					for i in range(16):
						if len(plaintext)-1 < i:
							ciphertext[i] = 0 ^ output[i]
						elif len(output)-1 < i:
							ciphertext[i] = plaintext[i] ^ 0
						elif len(plaintext)-1 < i and len(output) < i:
							ciphertext[i] = 0 ^ 0
						else:
							ciphertext[i] = plaintext[i] ^ output[i]
					for k in range(end-start):
						cipherOut.append(ciphertext[k])
					iput = output
				elif mode == self.modeOfOperation["CBC"]:
					for i in range(16):
						if firstRound:
							iput[i] =  plaintext[i] ^ IV[i]
						else:
							iput[i] =  plaintext[i] ^ ciphertext[i]
					# print 'IP@%s:%s' % (j, iput)
					firstRound = False
					ciphertext = self.aes.encrypt(iput, key, size)
					# always 16 bytes because of the padding for CBC
					for k in range(16):
						cipherOut.append(ciphertext[k])
		return mode, len(stringIn), cipherOut

	# Mode of Operation Decryption
	# cipherIn - Encrypted String
	# originalsize - The unencrypted string length - required for CBC
	# mode - mode of type modeOfOperation
	# key - a number array of the bit length size
	# size - the bit length of the key
	# IV - the 128 bit number array Initilization Vector
	def decrypt(self, cipherIn, originalsize, mode, key, size, IV):
		# cipherIn = unescCtrlChars(cipherIn)
		if len(key) % size:
			return None
		if len(IV) % 16:
			return None
		# the AES input/output
		ciphertext = []
		iput = []
		output = []
		plaintext = [0] * 16
		# the output plain text string
		stringOut = ''
		# char firstRound
		firstRound = True
		if cipherIn != None:
			for j in range(int(math.ceil(float(len(cipherIn))/16))):
				start = j*16
				end = j*16+16
				if j*16+16 > len(cipherIn):
					end = len(cipherIn)
				ciphertext = cipherIn[start:end]
				if mode == self.modeOfOperation["CFB"]:
					if firstRound:
						output = self.aes.encrypt(IV, key, size)
						firstRound = False
					else:
						output = self.aes.encrypt(iput, key, size)
					for i in range(16):
						if len(output)-1 < i:
							plaintext[i] = 0 ^ ciphertext[i]
						elif len(ciphertext)-1 < i:
							plaintext[i] = output[i] ^ 0
						elif len(output)-1 < i and len(ciphertext) < i:
							plaintext[i] = 0 ^ 0
						else:
							plaintext[i] = output[i] ^ ciphertext[i]
					for k in range(end-start):
						stringOut += chr(plaintext[k])
					iput = ciphertext
				elif mode == self.modeOfOperation["OFB"]:
					if firstRound:
						output = self.aes.encrypt(IV, key, size)
						firstRound = False
					else:
						output = self.aes.encrypt(iput, key, size)
					for i in range(16):
						if len(output)-1 < i:
							plaintext[i] = 0 ^ ciphertext[i]
						elif len(ciphertext)-1 < i:
							plaintext[i] = output[i] ^ 0
						elif len(output)-1 < i and len(ciphertext) < i:
							plaintext[i] = 0 ^ 0
						else:
							plaintext[i] = output[i] ^ ciphertext[i]
					for k in range(end-start):
						stringOut += chr(plaintext[k])
					iput = output
				elif mode == self.modeOfOperation["CBC"]:
					output = self.aes.decrypt(ciphertext, key, size)
					for i in range(16):
						if firstRound:
							plaintext[i] = IV[i] ^ output[i]
						else:
							plaintext[i] = iput[i] ^ output[i]
					firstRound = False
					if originalsize is not None and originalsize < end:
						for k in range(originalsize-start):
							stringOut += chr(plaintext[k])
					else:
						for k in range(end-start):
							stringOut += chr(plaintext[k])
					iput = ciphertext
		return stringOut

######################
# end of aes.py code #
######################

###################################
# pywallet crypter implementation #
###################################

crypter = None

try:
	from Crypto.Cipher import AES
	crypter = 'pycrypto'
except:
	pass

class Crypter_pycrypto( object ):
	def SetKeyFromPassphrase(self, vKeyData, vSalt, nDerivIterations, nDerivationMethod):
		if nDerivationMethod != 0:
			return 0
		data = vKeyData + vSalt
		for i in xrange(nDerivIterations):
			data = hashlib.sha512(data).digest()
		self.SetKey(data[0:32])
		self.SetIV(data[32:32+16])
		return len(data)

	def SetKey(self, key):
		self.chKey = key

	def SetIV(self, iv):
		self.chIV = iv[0:16]

	def Encrypt(self, data):
		return AES.new(self.chKey,AES.MODE_CBC,self.chIV).encrypt(data)[0:32]

	def Decrypt(self, data):
		return AES.new(self.chKey,AES.MODE_CBC,self.chIV).decrypt(data)[0:32]

try:
	if not crypter:
		import ctypes
		import ctypes.util
		ssl = ctypes.cdll.LoadLibrary (ctypes.util.find_library ('ssl') or 'libeay32')
		crypter = 'ssl'
except:
	pass

class Crypter_ssl(object):
	def __init__(self):
		self.chKey = ctypes.create_string_buffer (32)
		self.chIV = ctypes.create_string_buffer (16)

	def SetKeyFromPassphrase(self, vKeyData, vSalt, nDerivIterations, nDerivationMethod):
		if nDerivationMethod != 0:
			return 0
		strKeyData = ctypes.create_string_buffer (vKeyData)
		chSalt = ctypes.create_string_buffer (vSalt)
		return ssl.EVP_BytesToKey(ssl.EVP_aes_256_cbc(), ssl.EVP_sha512(), chSalt, strKeyData,
			len(vKeyData), nDerivIterations, ctypes.byref(self.chKey), ctypes.byref(self.chIV))

	def SetKey(self, key):
		self.chKey = ctypes.create_string_buffer(key)

	def SetIV(self, iv):
		self.chIV = ctypes.create_string_buffer(iv)

	def Encrypt(self, data):
		buf = ctypes.create_string_buffer(len(data) + 16)
		written = ctypes.c_int(0)
		final = ctypes.c_int(0)
		ctx = ssl.EVP_CIPHER_CTX_new()
		ssl.EVP_CIPHER_CTX_init(ctx)
		ssl.EVP_EncryptInit_ex(ctx, ssl.EVP_aes_256_cbc(), None, self.chKey, self.chIV)
		ssl.EVP_EncryptUpdate(ctx, buf, ctypes.byref(written), data, len(data))
		output = buf.raw[:written.value]
		ssl.EVP_EncryptFinal_ex(ctx, buf, ctypes.byref(final))
		output += buf.raw[:final.value]
		return output

	def Decrypt(self, data):
		buf = ctypes.create_string_buffer(len(data) + 16)
		written = ctypes.c_int(0)
		final = ctypes.c_int(0)
		ctx = ssl.EVP_CIPHER_CTX_new()
		ssl.EVP_CIPHER_CTX_init(ctx)
		ssl.EVP_DecryptInit_ex(ctx, ssl.EVP_aes_256_cbc(), None, self.chKey, self.chIV)
		ssl.EVP_DecryptUpdate(ctx, buf, ctypes.byref(written), data, len(data))
		output = buf.raw[:written.value]
		ssl.EVP_DecryptFinal_ex(ctx, buf, ctypes.byref(final))
		output += buf.raw[:final.value]
		return output

class Crypter_pure(object):
	def __init__(self):
		self.m = AESModeOfOperation()
		self.cbc = self.m.modeOfOperation["CBC"]
		self.sz = self.m.aes.keySize["SIZE_256"]

	def SetKeyFromPassphrase(self, vKeyData, vSalt, nDerivIterations, nDerivationMethod):
		if nDerivationMethod != 0:
			return 0
		data = vKeyData + vSalt
		for i in xrange(nDerivIterations):
			data = hashlib.sha512(data).digest()
		self.SetKey(data[0:32])
		self.SetIV(data[32:32+16])
		return len(data)

	def SetKey(self, key):
		self.chKey = [ord(i) for i in key]

	def SetIV(self, iv):
		self.chIV = [ord(i) for i in iv]

	def Encrypt(self, data):
		mode, size, cypher = self.m.encrypt(data, self.cbc, self.chKey, self.sz, self.chIV)
		return ''.join(map(chr, cypher))

	def Decrypt(self, data):
		chData = [ord(i) for i in data]
		return self.m.decrypt(chData, self.sz, self.cbc, self.chKey, self.sz, self.chIV)

if crypter == 'pycrypto':
	crypter = Crypter_pycrypto()
#	print "Crypter: pycrypto"
elif crypter == 'ssl':
	crypter = Crypter_ssl()
#	print "Crypter: ssl"
else:
	crypter = Crypter_pure()
#	print "Crypter: pure"
	logging.warning("pycrypto or libssl not found, decryption may be slow")

##########################################
# end of pywallet crypter implementation #
##########################################

# secp256k1

try:
	_p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2FL
except:
	print "Python 3 is not supported, you need Python 2.7.x"
	exit(1)
_r = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141L
_b = 0x0000000000000000000000000000000000000000000000000000000000000007L
_a = 0x0000000000000000000000000000000000000000000000000000000000000000L
_Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798L
_Gy = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8L

try:
	import ecdsa
	from ecdsa import der
	curve_secp256k1 = ecdsa.ellipticcurve.CurveFp (_p, _a, _b)
	generator_secp256k1 = g = ecdsa.ellipticcurve.Point (curve_secp256k1, _Gx, _Gy, _r)
	randrange = random.SystemRandom().randrange
	secp256k1 = ecdsa.curves.Curve ( "secp256k1", curve_secp256k1, generator_secp256k1, (1, 3, 132, 0, 10) )
	ecdsa.curves.curves.append (secp256k1)
except:
	missing_dep.append('ecdsa')

# python-ecdsa code (EC_KEY implementation)

class CurveFp( object ):
	def __init__( self, p, a, b ):
		self.__p = p
		self.__a = a
		self.__b = b

	def p( self ):
		return self.__p

	def a( self ):
		return self.__a

	def b( self ):
		return self.__b

	def contains_point( self, x, y ):
		return ( y * y - ( x * x * x + self.__a * x + self.__b ) ) % self.__p == 0

class Point( object ):
	def __init__( self, curve, x, y, order = None ):
		self.__curve = curve
		self.__x = x
		self.__y = y
		self.__order = order
		if self.__curve: assert self.__curve.contains_point( x, y )
		if order: assert self * order == INFINITY

	def __add__( self, other ):
		if other == INFINITY: return self
		if self == INFINITY: return other
		assert self.__curve == other.__curve
		if self.__x == other.__x:
			if ( self.__y + other.__y ) % self.__curve.p() == 0:
				return INFINITY
			else:
				return self.double()

		p = self.__curve.p()
		l = ( ( other.__y - self.__y ) * \
					inverse_mod( other.__x - self.__x, p ) ) % p
		x3 = ( l * l - self.__x - other.__x ) % p
		y3 = ( l * ( self.__x - x3 ) - self.__y ) % p
		return Point( self.__curve, x3, y3 )

	def __mul__( self, other ):
		def leftmost_bit( x ):
			assert x > 0
			result = 1L
			while result <= x: result = 2 * result
			return result / 2

		e = other
		if self.__order: e = e % self.__order
		if e == 0: return INFINITY
		if self == INFINITY: return INFINITY
		assert e > 0
		e3 = 3 * e
		negative_self = Point( self.__curve, self.__x, -self.__y, self.__order )
		i = leftmost_bit( e3 ) / 2
		result = self
		while i > 1:
			result = result.double()
			if ( e3 & i ) != 0 and ( e & i ) == 0: result = result + self
			if ( e3 & i ) == 0 and ( e & i ) != 0: result = result + negative_self
			i = i / 2
		return result

	def __rmul__( self, other ):
		return self * other

	def __str__( self ):
		if self == INFINITY: return "infinity"
		return "(%d,%d)" % ( self.__x, self.__y )

	def double( self ):
		if self == INFINITY:
			return INFINITY

		p = self.__curve.p()
		a = self.__curve.a()
		l = ( ( 3 * self.__x * self.__x + a ) * \
					inverse_mod( 2 * self.__y, p ) ) % p
		x3 = ( l * l - 2 * self.__x ) % p
		y3 = ( l * ( self.__x - x3 ) - self.__y ) % p
		return Point( self.__curve, x3, y3 )

	def x( self ):
		return self.__x

	def y( self ):
		return self.__y

	def curve( self ):
		return self.__curve

	def order( self ):
		return self.__order

INFINITY = Point( None, None, None )

def inverse_mod( a, m ):
	if a < 0 or m <= a: a = a % m
	c, d = a, m
	uc, vc, ud, vd = 1, 0, 0, 1
	while c != 0:
		q, c, d = divmod( d, c ) + ( c, )
		uc, vc, ud, vd = ud - q*uc, vd - q*vc, uc, vc
	assert d == 1
	if ud > 0: return ud
	else: return ud + m

class Signature( object ):
	def __init__( self, r, s ):
		self.r = r
		self.s = s

class Public_key( object ):
	def __init__( self, generator, point, c=None ):
		self.curve = generator.curve()
		self.generator = generator
		self.point = point
		self.compressed = c
		n = generator.order()
		if not n:
			raise RuntimeError, "Generator point must have order."
		if not n * point == INFINITY:
			raise RuntimeError, "Generator point order is bad."
		if point.x() < 0 or n <= point.x() or point.y() < 0 or n <= point.y():
			raise RuntimeError, "Generator point has x or y out of range."

	def verifies( self, hash, signature ):
		G = self.generator
		n = G.order()
		r = signature.r
		s = signature.s
		if r < 1 or r > n-1: return False
		if s < 1 or s > n-1: return False
		c = inverse_mod( s, n )
		u1 = ( hash * c ) % n
		u2 = ( r * c ) % n
		xy = u1 * G + u2 * self.point
		v = xy.x() % n
		return v == r

	def ser(self):
		if self.compressed:
			pk=('%02x'%(2+(self.point.y()&1))) + '%064x' % self.point.x()
		else:
			pk='04%064x%064x' % (self.point.x(), self.point.y())

		return pk.decode('hex')

	def get_addr(self, v=0):
		return public_key_to_bc_address(self.ser(), v)

class Private_key( object ):
	def __init__( self, public_key, secret_multiplier ):
		self.public_key = public_key
		self.secret_multiplier = secret_multiplier

	def der( self ):
		hex_der_key = '06052b8104000a30740201010420' + \
			'%064x' % self.secret_multiplier + \
			'a00706052b8104000aa14403420004' + \
			'%064x' % self.public_key.point.x() + \
			'%064x' % self.public_key.point.y()
		return hex_der_key.decode('hex')

	def sign( self, hash, random_k ):
		G = self.public_key.generator
		n = G.order()
		k = random_k % n
		p1 = k * G
		r = p1.x()
		if r == 0: raise RuntimeError, "amazingly unlucky random number r"
		s = ( inverse_mod( k, n ) * \
					( hash + ( self.secret_multiplier * r ) % n ) ) % n
		if s == 0: raise RuntimeError, "amazingly unlucky random number s"
		return Signature( r, s )

class EC_KEY(object):
	def __init__( self, secret ):
		curve = CurveFp( _p, _a, _b )
		generator = Point( curve, _Gx, _Gy, _r )
		self.pubkey = Public_key( generator, generator * secret )
		self.privkey = Private_key( self.pubkey, secret )
		self.secret = secret

# end of python-ecdsa code

# pywallet openssl private key implementation

def i2d_ECPrivateKey(pkey, compressed=False):#, crypted=True):
	part3='a081a53081a2020101302c06072a8648ce3d0101022100'  # for uncompressed keys
	if compressed:
		if True:#not crypted:  ## Bitcoin accepts both part3's for crypted wallets...
			part3='a08185308182020101302c06072a8648ce3d0101022100'  # for compressed keys
		key = '3081d30201010420' + \
			'%064x' % pkey.secret + \
			part3 + \
			'%064x' % _p + \
			'3006040100040107042102' + \
			'%064x' % _Gx + \
			'022100' + \
			'%064x' % _r + \
			'020101a124032200'
	else:
		key = '308201130201010420' + \
			'%064x' % pkey.secret + \
			part3 + \
			'%064x' % _p + \
			'3006040100040107044104' + \
			'%064x' % _Gx + \
			'%064x' % _Gy + \
			'022100' + \
			'%064x' % _r + \
			'020101a144034200'

	return key.decode('hex') + i2o_ECPublicKey(pkey, compressed)

def i2o_ECPublicKey(pkey, compressed=False):
	# public keys are 65 bytes long (520 bits)
	# 0x04 + 32-byte X-coordinate + 32-byte Y-coordinate
	# 0x00 = point at infinity, 0x02 and 0x03 = compressed, 0x04 = uncompressed
	# compressed keys: <sign> <x> where <sign> is 0x02 if y is even and 0x03 if y is odd
	if compressed:
		if pkey.pubkey.point.y() & 1:
			key = '03' + '%064x' % pkey.pubkey.point.x()
		else:
			key = '02' + '%064x' % pkey.pubkey.point.x()
	else:
		key = '04' + \
			'%064x' % pkey.pubkey.point.x() + \
			'%064x' % pkey.pubkey.point.y()

	return key.decode('hex')

# bitcointools hashes and base58 implementation

def hash_160(public_key):
 	md = hashlib.new('ripemd160')
	md.update(hashlib.sha256(public_key).digest())
	return md.digest()

def public_key_to_bc_address(public_key, v=None):
	if v==None:
		v=addrtype
	h160 = hash_160(public_key)
	return hash_160_to_bc_address(h160, v)

def hash_160_to_bc_address(h160, v=None):
	if v==None:
		v=addrtype
	vh160 = chr(v) + h160
	h = Hash(vh160)
	addr = vh160 + h[0:4]
	return b58encode(addr)

def bc_address_to_hash_160(addr):
	bytes = b58decode(addr, 25)
	return bytes[1:21]

__b58chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
__b58base = len(__b58chars)

def b58encode(v):
	" encode v, which is a string of bytes, to base58.
	"

	long_value = 0L
	for (i, c) in enumerate(v[::-1]):
		long_value += (256**i) * ord(c)

	result = ''
	while long_value >= __b58base:
		div, mod = divmod(long_value, __b58base)
		result = __b58chars[mod] + result
		long_value = div
	result = __b58chars[long_value] + result

	# Bitcoin does a little leading-zero-compression:
	# leading 0-bytes in the input become leading-1s
	nPad = 0
	for c in v:
		if c == '\0': nPad += 1
		else: break

	return (__b58chars[0]*nPad) + result

def b58decode(v, length):
	" decode v into a string of len bytes
	"
	long_value = 0L
	for (i, c) in enumerate(v[::-1]):
		long_value += __b58chars.find(c) * (__b58base**i)

	result = ''
	while long_value >= 256:
		div, mod = divmod(long_value, 256)
		result = chr(mod) + result
		long_value = div
	result = chr(long_value) + result

	nPad = 0
	for c in v:
		if c == __b58chars[0]: nPad += 1
		else: break

	result = chr(0)*nPad + result
	if length is not None and len(result) != length:
		return None

	return result

# end of bitcointools base58 implementation

# address handling code

def long_hex(bytes):
	return bytes.encode('hex_codec')

def Hash(data):
	return hashlib.sha256(hashlib.sha256(data).digest()).digest()

def EncodeBase58Check(secret):
	hash = Hash(secret)
	return b58encode(secret + hash[0:4])

def DecodeBase58Check(sec):
	vchRet = b58decode(sec, None)
	secret = vchRet[0:-4]
	csum = vchRet[-4:]
	hash = Hash(secret)
	cs32 = hash[0:4]
	if cs32 != csum:
		return None
	else:
		return secret

def str_to_long(b):
	res = 0
	pos = 1
	for a in reversed(b):
		res += ord(a) * pos
		pos *= 256
	return res

def PrivKeyToSecret(privkey):
	if len(privkey) == 279:
		return privkey[9:9+32]
	else:
		return privkey[8:8+32]

def SecretToASecret(secret, compressed=False):
	prefix = chr((addrtype+128)&255)
	if addrtype==48:  #assuming Litecoin
		prefix = chr(128)
	vchIn = prefix + secret
	if compressed: vchIn += '\01'
	return EncodeBase58Check(vchIn)

def ASecretToSecret(sec):
	vch = DecodeBase58Check(sec)
	if not vch:
		return False
	if vch[0] != chr((addrtype+128)&255):
		print 'Warning: adress prefix seems bad (%d vs %d)'%(ord(vch[0]), (addrtype+128)&255)
	return vch[1:]

def regenerate_key(sec):
	b = ASecretToSecret(sec)
	if not b:
		return False
	b = b[0:32]
	secret = int('0x' + b.encode('hex'), 16)
	return EC_KEY(secret)

def GetPubKey(pkey, compressed=False):
	return i2o_ECPublicKey(pkey, compressed)

def GetPrivKey(pkey, compressed=False):
	return i2d_ECPrivateKey(pkey, compressed)

def GetSecret(pkey):
	return ('%064x' % pkey.secret).decode('hex')

def is_compressed(sec):
	b = ASecretToSecret(sec)
	return len(b) == 33

# bitcointools wallet.dat handling code

def parse_CAddress(vds):
	d = {'ip':'0.0.0.0','port':0,'nTime': 0}
	try:
		d['nVersion'] = vds.read_int32()
		d['nTime'] = vds.read_uint32()
		d['nServices'] = vds.read_uint64()
		d['pchReserved'] = vds.read_bytes(12)
		d['ip'] = socket.inet_ntoa(vds.read_bytes(4))
		d['port'] = vds.read_uint16()
	except:
		pass
	return d

def deserialize_CAddress(d):
	return d['ip']+":"+str(d['port'])

def parse_BlockLocator(vds):
	d = { 'hashes' : [] }
	nHashes = vds.read_compact_size()
	for i in xrange(nHashes):
		d['hashes'].append(vds.read_bytes(32))
		return d

def deserialize_BlockLocator(d):
  result = "Block Locator top: "+d['hashes'][0][::-1].encode('hex_codec')
  return result

def parse_setting(setting, vds):
	if setting[0] == "f":	# flag (boolean) settings
		return str(vds.read_boolean())
	elif setting[0:4] == "addr": # CAddress
		d = parse_CAddress(vds)
		return deserialize_CAddress(d)
	elif setting == "nTransactionFee":
		return vds.read_int64()
	elif setting == "nLimitProcessors":
		return vds.read_int32()
	return 'unknown setting'

class SerializationError(Exception):
	"Thrown when there's a problem deserializing or serializing"


def search_patterns_on_disk(device, size, inc, patternlist):   # inc must be higher than 1k
	try:
		otype=os.O_RDONLY|os.O_BINARY
	except:
		otype=os.O_RDONLY
	try:
		fd = os.open(device, otype)
	except Exception as e:
		print "Can't open %s, check the path or try as root"%device
		print "  Error:", e.args
		exit(0)

	i = 0
	data=''

	tzero=time.time()
	sizetokeep=0
	BlocksToInspect=dict(map(lambda x:[x,[]], patternlist))
	syst=systype()
	lendataloaded=None
	writeProgressEvery=100*Mo
	while i < int(size) and (lendataloaded!=0 or lendataloaded==None):
		if int(i/writeProgressEvery)!=int((i+inc)/writeProgressEvery):
			print "%.2f Go read"%(i/1e9)
		try:
			datakept=data[-sizetokeep:]
			data = datakept+os.read(fd, inc)
			lendataloaded = len(data)-len(datakept)   #should be inc
			for text in patternlist:
				if text in data:
					BlocksToInspect[text].append([i-len(datakept), data, len(datakept)])
					pass
			sizetokeep=20   # 20 because all the patterns have a len<20. Could be higher.
			i += lendataloaded
		except Exception as exc:
			if lendataloaded%512>0:
				raise Exception("SPOD error 1: %d, %d"%(lendataloaded, i-len(datakept)))
			os.lseek(fd, lendataloaded, os.SEEK_CUR)
			print str(exc)
			i += lendataloaded
			continue
	os.close(fd)

	AllOffsets=dict(map(lambda x:[x,[]], patternlist))
	for text,blocks in BlocksToInspect.items():
		for offset,data,ldk in blocks:  #ldk = len(datakept)
			offsetslist=[offset+m.start() for m in re.finditer(text, data)]
			AllOffsets[text].extend(offsetslist)

	AllOffsets['PRFdevice']=device
	AllOffsets['PRFdt']=time.time()-tzero
	AllOffsets['PRFsize']=i
	return AllOffsets

def multiextract(s, ll):
	r=[]
	cursor=0
	for length in ll:
		r.append(s[cursor:cursor+length])
		cursor+=length
	if s[cursor:]!='':
		r.append(s[cursor:])
	return r

class RecovCkey(object):
	def __init__(self, epk, pk):
		self.encrypted_pk=epk
		self.public_key=pk
		self.mkey=None
		self.privkey=None


class RecovMkey(object):
	def __init__(self, ekey, salt, nditer, ndmethod, nid):
		self.encrypted_key=ekey
		self.salt=salt
		self.iterations=nditer
		self.method=ndmethod
		self.id=nid

def readpartfile(fd, offset, length):   #make everything 512*n because of windows...
	rest=offset%512
	new_offset=offset-rest
	big_length=512*(int((length+rest-1)/512)+1)
	os.lseek(fd, new_offset, os.SEEK_SET)
	d=os.read(fd, big_length)
	return d[rest:rest+length]

def recov_ckey(fd, offset):
	d=readpartfile(fd, offset-49, 122)
	me=multiextract(d, [1,48,4,4,1])

	checks=[]
	checks.append([0, '30'])
	checks.append([3, '636b6579'])
	if sum(map(lambda x:int(me[x[0]]!=x[1].decode('hex')), checks)):  #number of false statements
		return None

	return me

def recov_mkey(fd, offset):
	d=readpartfile(fd, offset-72, 84)
	me=multiextract(d, [4,48,1,8,4,4,1,2,8,4])

	checks=[]
	checks.append([0, '43000130'])
	checks.append([2, '08'])
	checks.append([6, '00'])
	checks.append([8, '090001046d6b6579'])
	if sum(map(lambda x:int(me[x[0]]!=x[1].decode('hex')), checks)):  #number of false statements
		return None

	return me

def recov_uckey(fd, offset):
	checks=[]

	d=readpartfile(fd, offset-217, 223)
	if d[-7]=='\x26':
		me=multiextract(d, [2,1,4,1,32,141,33,2,1,6])

		checks.append([0, '3081'])
		checks.append([2, '02010104'])
	elif d[-7]=='\x46':
		d=readpartfile(fd, offset-282, 286)

		me=multiextract(d, [2,1,4,1,32,173,65,1,2,5])

		checks.append([0, '8201'])
		checks.append([2, '02010104'])
		checks.append([-1, '460001036b'])
	else:
		return None


	if sum(map(lambda x:int(me[x[0]]!=x[1].decode('hex')), checks)):  #number of false statements
		return None

	return me

def starts_with(s, b):
	return len(s)>=len(b) and s[:len(b)]==b


def recov(device, passes, size=102400, inc=10240, outputdir='.'):
	if inc%512>0:
		inc-=inc%512   #inc must be 512*n on Windows... Don't ask me why...

	nameToDBName={'mkey':'\x09\x00\x01\x04mkey','ckey':'\x27\x00\x01\x04ckey','key':'\x00\x01\x03key',}


	if not starts_with(device, 'PartialRecoveryFile:'):
		r=search_patterns_on_disk(device, size, inc, map(lambda x:nameToDBName[x], ['mkey', 'ckey', 'key']))
		f=open(outputdir+'/pywallet_partial_recovery_%d.dat'%ts(), 'w')
		f.write(str(r))
		f.close()
		print "\nRead %.1f Go in %.1f minutes\n"%(r['PRFsize']/1e9, r['PRFdt']/60.0)
	else:
		prf=device[20:]
		f=open(prf, 'r')
		content=f.read()
		f.close()
		cmd=("z = "+content+"")
		exec cmd in locals()
		r=z
		device=r['PRFdevice']
		print "\nLoaded %.1f Go from %s\n"%(r['PRFsize']/1e9, device)


	try:
		otype=os.O_RDONLY|os.O_BINARY
	except:
		otype=os.O_RDONLY
	fd = os.open(device, otype)


	mkeys=[]
	crypters=[]
	syst=systype()
	for offset in r[nameToDBName['mkey']]:
		s=recov_mkey(fd, offset)
		if s==None:
			continue
		newmkey=RecovMkey(s[1],s[3],int(s[5][::-1].encode('hex'), 16),int(s[4][::-1].encode('hex'), 16),int(s[-1][::-1].encode('hex'), 16))
		mkeys.append([offset,newmkey])

	print "Found", len(mkeys), 'possible wallets'




	ckeys=[]
	for offset in r[nameToDBName['ckey']]:
		s=recov_ckey(fd, offset)
		if s==None:
			continue
		newckey=RecovCkey(s[1], s[5][:int(s[4].encode('hex'),16)])
		ckeys.append([offset,newckey])
	print "Found", len(ckeys), 'possible encrypted keys'


	uckeys=[]
	for offset in r[nameToDBName['key']]:
		s=recov_uckey(fd, offset)
		if s==None:
			continue
		uckeys.append(s[4])
	print "Found", len(uckeys), 'possible unencrypted keys'


	os.close(fd)


	list_of_possible_keys_per_master_key=dict(map(lambda x:[x[1],[]], mkeys))
	for cko,ck in ckeys:
		tl=map(lambda x:[abs(x[0]-cko)]+x, mkeys)
		tl=sorted(tl, key=lambda x:x[0])
		list_of_possible_keys_per_master_key[tl[0][2]].append(ck)

	cpt=0
	mki=1
	tzero=time.time()
	if len(passes)==0:
		if len(ckeys)>0:
			print "Can't decrypt them as you didn't provide any passphrase."
	else:
		for mko,mk in mkeys:
			list_of_possible_keys=list_of_possible_keys_per_master_key[mk]
			sys.stdout.write( "\nPossible wallet #"+str(mki))
			sys.stdout.flush()
			for ppi,pp in enumerate(passes):
				sys.stdout.write( "\n    with passphrase #"+str(ppi+1)+"  ")
				sys.stdout.flush()
				failures_in_a_row=0
#				print "SKFP params:", pp, mk.salt, mk.iterations, mk.method
				res = crypter.SetKeyFromPassphrase(pp, mk.salt, mk.iterations, mk.method)
				if res == 0:
					print "Unsupported derivation method"
					sys.exit(1)
				masterkey = crypter.Decrypt(mk.encrypted_key)
				crypter.SetKey(masterkey)
				for ck in list_of_possible_keys:
					if cpt%10==9 and failures_in_a_row==0:
						sys.stdout.write('.')
						sys.stdout.flush()
					if failures_in_a_row>5:
						break
					crypter.SetIV(Hash(ck.public_key))
					secret = crypter.Decrypt(ck.encrypted_pk)
					compressed = ck.public_key[0] != '\04'


					pkey = EC_KEY(int('0x' + secret.encode('hex'), 16))
					if ck.public_key != GetPubKey(pkey, compressed):
						failures_in_a_row+=1
					else:
						failures_in_a_row=0
						ck.mkey=mk
						ck.privkey=secret
					cpt+=1
			mki+=1
		print "\n"
		tone=time.time()
		try:
			calcspeed=1.0*cpt/(tone-tzero)*60  #calc/min
		except:
			calcspeed=1.0
		if calcspeed==0:
			calcspeed=1.0

		ckeys_not_decrypted=filter(lambda x:x[1].privkey==None, ckeys)
		refused_to_test_all_pps=True
		if len(ckeys_not_decrypted)==0:
			print "All the found encrypted private keys have been decrypted."
			return map(lambda x:x[1].privkey, ckeys)
		else:
			print "Private keys not decrypted: %d"%len(ckeys_not_decrypted)
			print "Trying all the remaining possibilities (%d) might take up to %d minutes."%(len(ckeys_not_decrypted)*len(passes)*len(mkeys),int(len(ckeys_not_decrypted)*len(passes)*len(mkeys)/calcspeed))
			cont=raw_input("Do you want to test them? (y/n): ")
			while len(cont)==0:
                                cont=raw_input("Do you want to test them? (y/n): ")
                        if cont[0]=='y':
                                refused_to_test_all_pps=False
                                cpt=0
                                for dist,mko,mk in tl:
                                        for ppi,pp in enumerate(passes):
                                                res = crypter.SetKeyFromPassphrase(pp, mk.salt, mk.iterations, mk.method)
                                                if res == 0:
                                                        logging.error("Unsupported derivation method")
                                                        sys.exit(1)
                                                masterkey = crypter.Decrypt(mk.encrypted_key)
                                                crypter.SetKey(masterkey)
                                                for cko,ck in ckeys_not_decrypted:
                                                        tl=map(lambda x:[abs(x[0]-cko)]+x, mkeys)
                                                        tl=sorted(tl, key=lambda x:x[0])
                                                        if mk==tl[0][2]:
                                                                continue         #because already tested
                                                        crypter.SetIV(Hash(ck.public_key))
                                                        secret = crypter.Decrypt(ck.encrypted_pk)
                                                        compressed = ck.public_key[0] != '\04'


                                                        pkey = EC_KEY(int('0x' + secret.encode('hex'), 16))
                                                        if ck.public_key == GetPubKey(pkey, compressed):
                                                                ck.mkey=mk
                                                                ck.privkey=secret
                                                        cpt+=1

		print
		ckeys_not_decrypted=filter(lambda x:x[1].privkey==None, ckeys)
		if len(ckeys_not_decrypted)==0:
			print "All the found encrypted private keys have been finally decrypted."
		elif not refused_to_test_all_pps:
			print "Private keys not decrypted: %d"%len(ckeys_not_decrypted)
			print "Try another password, check the size of your partition or seek help"


	uncrypted_ckeys=filter(lambda x:x!=None, map(lambda x:x[1].privkey, ckeys))
	uckeys.extend(uncrypted_ckeys)

	return uckeys




def ts():
	return int(time.mktime(datetime.now().timetuple()))

def check_postkeys(key, postkeys):
	for i in postkeys:
		if key[:len(i)] == i:
			return True
	return False

def one_element_in(a, string):
	for i in a:
		if i in string:
			return True
	return False

def first_read(device, size, prekeys, inc=10000):
	t0 = ts()-1
	try:
		fd = os.open (device, os.O_RDONLY)
	except:
		print("Can't open %s, check the path or try as root"%device)
		exit(0)
	prekey = prekeys[0]
	data = ""
	i = 0
	data = os.read (fd, i)
	before_contained_key = False
	contains_key = False
	ranges = []

	while i < int(size):
		if i%(10*Mio) > 0 and i%(10*Mio) <= inc:
			print("\n%.2f/%.2f Go"%(i/1e9, size/1e9))
			t = ts()
			speed = i/(t-t0)
			ETAts = size/speed + t0
			d = datetime.fromtimestamp(ETAts)
			print(d.strftime("   ETA: %H:%M:%S"))

		try:
			data = os.read (fd, inc)
		except Exception as exc:
			os.lseek(fd, inc, os.SEEK_CUR)
			print str(exc)
			i += inc
			continue

		contains_key = one_element_in(prekeys, data)

		if not before_contained_key and contains_key:
			ranges.append(i)

		if before_contained_key and not contains_key:
			ranges.append(i)

		before_contained_key = contains_key

		i += inc

	os.close (fd)
	return ranges

def shrink_intervals(device, ranges, prekeys, inc=1000):
	prekey = prekeys[0]
	nranges = []
	fd = os.open (device, os.O_RDONLY)
	for j in range(len(ranges)/2):
		before_contained_key = False
		contains_key = False
		bi = ranges[2*j]
		bf = ranges[2*j+1]

		mini_blocks = []
		k = bi
		while k <= bf + len(prekey) + 1:
			mini_blocks.append(k)
			k += inc
			mini_blocks.append(k)

		for k in range(len(mini_blocks)/2):
			mini_blocks[2*k] -= len(prekey) +1
			mini_blocks[2*k+1] += len(prekey) +1


			bi = mini_blocks[2*k]
			bf = mini_blocks[2*k+1]

			os.lseek(fd, bi, 0)

			data = os.read(fd, bf-bi+1)
			contains_key = one_element_in(prekeys, data)

			if not before_contained_key and contains_key:
				nranges.append(bi)

			if before_contained_key and not contains_key:
				nranges.append(bi+len(prekey) +1+len(prekey) +1)

			before_contained_key = contains_key

	os.close (fd)

	return nranges

def find_offsets(device, ranges, prekeys):
	prekey = prekeys[0]
	list_offsets = []
	to_read = 0
	fd = os.open (device, os.O_RDONLY)
	for i in range(len(ranges)/2):
		bi = ranges[2*i]-len(prekey)-1
		os.lseek(fd, bi, 0)
		bf = ranges[2*i+1]+len(prekey)+1
		to_read += bf-bi+1
		buf = ""
		for j in range(len(prekey)):
			buf += "\x00"
		curs = bi

		while curs <= bf:
			data = os.read(fd, 1)
			buf = buf[1:] + data
			if buf in prekeys:
				list_offsets.append(curs)
			curs += 1

	os.close (fd)

	return [to_read, list_offsets]

def read_keys(device, list_offsets):
	found_hexkeys = []
	fd = os.open (device, os.O_RDONLY)
	for offset in list_offsets:
		os.lseek(fd, offset+1, 0)
		data = os.read(fd, 40)
		hexkey = data[1:33].encode('hex')
		after_key = data[33:39].encode('hex')
		if hexkey not in found_hexkeys and check_postkeys(after_key.decode('hex'), postkeys):
			found_hexkeys.append(hexkey)

	os.close (fd)

	return found_hexkeys

def read_device_size(size):
	if size[-2] == 'i':
		unit = size[-3:]
		value = float(size[:-3])
	else:
		unit = size[-2:]
		value = float(size[:-2])
	exec 'unit = %s' % unit
	return int(value * unit)

def md5_2(a):
	return hashlib.md5(a).digest()

def md5_file(nf):
  try:
	fichier = file(nf, 'r').read()
	return md5_2(fichier)
  except:
	return 'zz'

def md5_onlinefile(add):
	page = urllib.urlopen(add).read()
	return md5_2(page)


class KEY:

	 def __init__ (self):
		  self.prikey = None
		  self.pubkey = None

	 def generate (self, secret=None):
		  if secret:
				exp = int ('0x' + secret.encode ('hex'), 16)
				self.prikey = ecdsa.SigningKey.from_secret_exponent (exp, curve=secp256k1)
		  else:
				self.prikey = ecdsa.SigningKey.generate (curve=secp256k1)
		  self.pubkey = self.prikey.get_verifying_key()
		  return self.prikey.to_der()

	 def set_privkey (self, key):
		  if len(key) == 279:
				seq1, rest = der.remove_sequence (key)
				integer, rest = der.remove_integer (seq1)
				octet_str, rest = der.remove_octet_string (rest)
				tag1, cons1, rest, = der.remove_constructed (rest)
				tag2, cons2, rest, = der.remove_constructed (rest)
				point_str, rest = der.remove_bitstring (cons2)
				self.prikey = ecdsa.SigningKey.from_string(octet_str, curve=secp256k1)
		  else:
				self.prikey = ecdsa.SigningKey.from_der (key)

	 def set_pubkey (self, key):
		  key = key[1:]
		  self.pubkey = ecdsa.VerifyingKey.from_string (key, curve=secp256k1)

	 def get_privkey (self):
		  _p = self.prikey.curve.curve.p ()
		  _r = self.prikey.curve.generator.order ()
		  _Gx = self.prikey.curve.generator.x ()
		  _Gy = self.prikey.curve.generator.y ()
		  encoded_oid2 = der.encode_oid (*(1, 2, 840, 10045, 1, 1))
		  encoded_gxgy = "\x04" + ("%64x" % _Gx).decode('hex') + ("%64x" % _Gy).decode('hex')
		  param_sequence = der.encode_sequence (
				ecdsa.der.encode_integer(1),
					der.encode_sequence (
					encoded_oid2,
					der.encode_integer (_p),
				),
				der.encode_sequence (
					der.encode_octet_string("\x00"),
					der.encode_octet_string("\x07"),
				),
				der.encode_octet_string (encoded_gxgy),
				der.encode_integer (_r),
				der.encode_integer (1),
		  );
		  encoded_vk = "\x00\x04" + self.pubkey.to_string ()
		  return der.encode_sequence (
				der.encode_integer (1),
				der.encode_octet_string (self.prikey.to_string ()),
				der.encode_constructed (0, param_sequence),
				der.encode_constructed (1, der.encode_bitstring (encoded_vk)),
		  )

	 def get_pubkey (self):
		  return "\x04" + self.pubkey.to_string()

	 def sign (self, hash):
		  sig = self.prikey.sign_digest (hash, sigencode=ecdsa.util.sigencode_der)
		  return sig.encode('hex')

	 def verify (self, hash, sig):
		  return self.pubkey.verify_digest (sig, hash, sigdecode=ecdsa.util.sigdecode_der)

def bool_to_int(b):
	if b:
		return 1
	return 0

class BCDataStream(object):
	def __init__(self):
		self.input = None
		self.read_cursor = 0

	def clear(self):
		self.input = None
		self.read_cursor = 0

	def write(self, bytes):	# Initialize with string of bytes
		if self.input is None:
			self.input = bytes
		else:
			self.input += bytes

	def map_file(self, file, start):	# Initialize with bytes from file
		self.input = mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ)
		self.read_cursor = start
	def seek_file(self, position):
		self.read_cursor = position
	def close_file(self):
		self.input.close()

	def read_string(self):
		# Strings are encoded depending on length:
		# 0 to 252 :	1-byte-length followed by bytes (if any)
		# 253 to 65,535 : byte'253' 2-byte-length followed by bytes
		# 65,536 to 4,294,967,295 : byte '254' 4-byte-length followed by bytes
		# ... and the Bitcoin client is coded to understand:
		# greater than 4,294,967,295 : byte '255' 8-byte-length followed by bytes of string
		# ... but I don't think it actually handles any strings that big.
		if self.input is None:
			raise SerializationError("call write(bytes) before trying to deserialize")

		try:
			length = self.read_compact_size()
		except IndexError:
			raise SerializationError("attempt to read past end of buffer")

		return self.read_bytes(length)

	def write_string(self, string):
		# Length-encoded as with read-string
		self.write_compact_size(len(string))
		self.write(string)

	def read_bytes(self, length):
		try:
			result = self.input[self.read_cursor:self.read_cursor+length]
			self.read_cursor += length
			return result
		except IndexError:
			raise SerializationError("attempt to read past end of buffer")

		return ''

	def read_boolean(self): return self.read_bytes(1)[0] != chr(0)
	def read_int16(self): return self._read_num('<h')
	def read_uint16(self): return self._read_num('<H')
	def read_int32(self): return self._read_num('<i')
	def read_uint32(self): return self._read_num('<I')
	def read_int64(self): return self._read_num('<q')
	def read_uint64(self): return self._read_num('<Q')

	def write_boolean(self, val): return self.write(chr(bool_to_int(val)))
	def write_int16(self, val): return self._write_num('<h', val)
	def write_uint16(self, val): return self._write_num('<H', val)
	def write_int32(self, val): return self._write_num('<i', val)
	def write_uint32(self, val): return self._write_num('<I', val)
	def write_int64(self, val): return self._write_num('<q', val)
	def write_uint64(self, val): return self._write_num('<Q', val)

	def read_compact_size(self):
		size = ord(self.input[self.read_cursor])
		self.read_cursor += 1
		if size == 253:
			size = self._read_num('<H')
		elif size == 254:
			size = self._read_num('<I')
		elif size == 255:
			size = self._read_num('<Q')
		return size

	def write_compact_size(self, size):
		if size < 0:
			raise SerializationError("attempt to write size < 0")
		elif size < 253:
			 self.write(chr(size))
		elif size < 2**16:
			self.write('\xfd')
			self._write_num('<H', size)
		elif size < 2**32:
			self.write('\xfe')
			self._write_num('<I', size)
		elif size < 2**64:
			self.write('\xff')
			self._write_num('<Q', size)

	def _read_num(self, format):
		(i,) = struct.unpack_from(format, self.input, self.read_cursor)
		self.read_cursor += struct.calcsize(format)
		return i

	def _write_num(self, format, num):
		s = struct.pack(format, num)
		self.write(s)



def inversetxid(txid):
	if len(txid) is not 64:
		print("Bad txid")
		return "CORRUPTEDTXID:"+txid
#		exit(0)
	new_txid = ""
	for i in range(32):
		new_txid += txid[62-2*i];
		new_txid += txid[62-2*i+1];
	return new_txid

def parse_wallet(db, item_callback):
	kds = BCDataStream()
	vds = BCDataStream()


	def parse_TxIn(vds):
		d = {}
		d['prevout_hash'] = vds.read_bytes(32).encode('hex')
		d['prevout_n'] = vds.read_uint32()
		d['scriptSig'] = vds.read_bytes(vds.read_compact_size()).encode('hex')
		d['sequence'] = vds.read_uint32()
		return d


	def parse_TxOut(vds):
		d = {}
		d['value'] = vds.read_int64()/1e8
		d['scriptPubKey'] = vds.read_bytes(vds.read_compact_size()).encode('hex')
		return d


	for (key, value) in db.items():
		d = { }

		kds.clear(); kds.write(key)
		vds.clear(); vds.write(value)

		type = kds.read_string()

		d["__key__"] = key
		d["__value__"] = value
		d["__type__"] = type

		try:
			if type == "tx":
				d["tx_id"] = inversetxid(kds.read_bytes(32).encode('hex_codec'))
				start = vds.read_cursor
				d['version'] = vds.read_int32()
				n_vin = vds.read_compact_size()
				d['txIn'] = []
				for i in xrange(n_vin):
					d['txIn'].append(parse_TxIn(vds))
				n_vout = vds.read_compact_size()
				d['txOut'] = []
				for i in xrange(n_vout):
					d['txOut'].append(parse_TxOut(vds))
				d['lockTime'] = vds.read_uint32()
				d['tx'] = vds.input[start:vds.read_cursor].encode('hex_codec')
				d['txv'] = value.encode('hex_codec')
				d['txk'] = key.encode('hex_codec')
			elif type == "name":
				d['hash'] = kds.read_string()
				d['name'] = vds.read_string()
			elif type == "version":
				d['version'] = vds.read_uint32()
			elif type == "minversion":
				d['minversion'] = vds.read_uint32()
			elif type == "setting":
				d['setting'] = kds.read_string()
				d['value'] = parse_setting(d['setting'], vds)
			elif type == "key":
				d['public_key'] = kds.read_bytes(kds.read_compact_size())
				d['private_key'] = vds.read_bytes(vds.read_compact_size())
			elif type == "wkey":
				d['public_key'] = kds.read_bytes(kds.read_compact_size())
				d['private_key'] = vds.read_bytes(vds.read_compact_size())
				d['created'] = vds.read_int64()
				d['expires'] = vds.read_int64()
				d['comment'] = vds.read_string()
			elif type == "defaultkey":
				d['key'] = vds.read_bytes(vds.read_compact_size())
			elif type == "pool":
				d['n'] = kds.read_int64()
				d['nVersion'] = vds.read_int32()
				d['nTime'] = vds.read_int64()
				d['public_key'] = vds.read_bytes(vds.read_compact_size())
			elif type == "acc":
				d['account'] = kds.read_string()
				d['nVersion'] = vds.read_int32()
				d['public_key'] = vds.read_bytes(vds.read_compact_size())
			elif type == "acentry":
				d['account'] = kds.read_string()
				d['n'] = kds.read_uint64()
				d['nVersion'] = vds.read_int32()
				d['nCreditDebit'] = vds.read_int64()
				d['nTime'] = vds.read_int64()
				d['otherAccount'] = vds.read_string()
				d['comment'] = vds.read_string()
			elif type == "bestblock":
				d['nVersion'] = vds.read_int32()
				d.update(parse_BlockLocator(vds))
			elif type == "ckey":
				d['public_key'] = kds.read_bytes(kds.read_compact_size())
				d['encrypted_private_key'] = vds.read_bytes(vds.read_compact_size())
			elif type == "mkey":
				d['nID'] = kds.read_uint32()
				d['encrypted_key'] = vds.read_string()
				d['salt'] = vds.read_string()
				d['nDerivationMethod'] = vds.read_uint32()
				d['nDerivationIterations'] = vds.read_uint32()
				d['otherParams'] = vds.read_string()

			item_callback(type, d)

		except Exception, e:
			traceback.print_exc()
			print("ERROR parsing wallet.dat, type %s" % type)
			print("key data: %s"%key)
			print("key data in hex: %s"%key.encode('hex_codec'))
			print("value data in hex: %s"%value.encode('hex_codec'))
			sys.exit(1)

def delete_from_wallet(db_env, walletfile, typedel, kd):
	db = open_wallet(db_env, walletfile, True)
	kds = BCDataStream()
	vds = BCDataStream()

	deleted_items = 0

	if not isinstance(kd, list):
		kd=[kd]

	if typedel=='tx' and kd!=['all']:
		for keydel in kd:
			db.delete('\x02\x74\x78'+keydel.decode('hex')[::-1])
			deleted_items+=1

	else:
		for i,keydel in enumerate(kd):
			for (key, value) in db.items():
				kds.clear(); kds.write(key)
				vds.clear(); vds.write(value)
				type = kds.read_string()

				if typedel == "tx" and type == "tx":
					db.delete(key)
					deleted_items+=1
				elif typedel == "key":
					if type == "key" or type == "ckey":
						if keydel == public_key_to_bc_address(kds.read_bytes(kds.read_compact_size())):
							db.delete(key)
							deleted_items+=1
					elif type == "pool":
						vds.read_int32()
						vds.read_int64()
						if keydel == public_key_to_bc_address(vds.read_bytes(vds.read_compact_size())):
							db.delete(key)
							deleted_items+=1
					elif type == "name":
						if keydel == kds.read_string():
							db.delete(key)
							deleted_items+=1


	db.close()
	return deleted_items

def merge_keys_lists(la, lb):
	lr={}
	llr=[]
	for k in la:
		lr[k[0]]=k[1]

	for k in lb:
		if k[0] in lr.keys():
			lr[k[0]]=lr[k[0]]+" / "+k[1]
		else:
			lr[k[0]]=k[1]

	for k,j in lr.items():
		llr.append([k,j])

	return llr

def merge_wallets(wadir, wa, wbdir, wb, wrdir, wr, passphrase_a, passphrase_b, passphrase_r):
	global passphrase
	passphrase_LAST=passphrase

	#Read Wallet 1
	passphrase=passphrase_a
	dba_env = create_env(wadir)
	crypted_a = read_wallet(json_db, dba_env, wa, True, True, "", None)['crypted']

	list_keys_a=[]
	for i in json_db['keys']:
		try:
			label=i['label']
		except:
			label="#Reserve"
		try:
			list_keys_a.append([i['secret'], label])
		except:
			pass

	if len(list_keys_a)==0:
		return [False, "Something went wrong with the first wallet."]


	#Read Wallet 2
	passphrase=passphrase_b
	dbb_env = create_env(wbdir)
	crypted_b = read_wallet(json_db, dbb_env, wb, True, True, "", None)['crypted']

	list_keys_b=[]
	for i in json_db['keys']:
		try:
			label=i['label']
		except:
			label="#Reserve"
		try:
			list_keys_b.append([i['secret'], label])
		except:
			pass
	if len(list_keys_b)==0:
		return [False, "Something went wrong with the second wallet."]

	m=merge_keys_lists(list_keys_a,list_keys_b)


	#Create new wallet
	dbr_env = create_env(wrdir)
	create_new_wallet(dbr_env, wr, 80100)

	dbr = open_wallet(dbr_env, wr, True)
	update_wallet(dbr, 'minversion', { 'minversion' : 60000})


	if len(passphrase_r)>0:
		NPP_salt=random_string(16).decode('hex')
		NPP_rounds=int(50000+random.random()*20000)
		NPP_method=0
		NPP_MK=random_string(64).decode('hex')

		crypter.SetKeyFromPassphrase(passphrase_r, NPP_salt, NPP_rounds, NPP_method)
		NPP_EMK = crypter.Encrypt(NPP_MK)

		update_wallet(dbr, 'mkey', {
		    "encrypted_key": NPP_EMK,
			'nDerivationIterations' : NPP_rounds,
			'nDerivationMethod' : NPP_method,
			'nID' : 1,
			'otherParams' : ''.decode('hex'),
		    "salt": NPP_salt
		})


	dbr.close()

	t='\n'.join(map(lambda x:';'.join(x), m))
	passphrase=passphrase_r

	global global_merging_message

	global_merging_message=["Merging...","Merging..."]
	thread.start_new_thread(import_csv_keys, ("\x00"+t, wrdir, wr,))
	t=""

	passphrase=passphrase_LAST

	return [True]

def random_string(l, alph="0123456789abcdef"):
	r=""
	la=len(alph)
	for i in range(l):
		r+=alph[int(la*(random.random()))]
	return r

def update_wallet(db, types, datas, paramsAreLists=False):
	"Write a single item to the wallet.
	db must be open with writable=True.
	type and data are the type code and data dictionary as parse_wallet would
	give to item_callback.
	data's __key__, __value__ and __type__ are ignored; only the primary data
	fields are used.
	"

	if not paramsAreLists:
		types=[types]
		datas=[datas]

	if len(types)!=len(datas):
		raise Exception("UpdateWallet: sizes are different")

	for it,type in enumerate(types):
		data=datas[it]

		d = data
		kds = BCDataStream()
		vds = BCDataStream()

		# Write the type code to the key
		kds.write_string(type)
		vds.write("")						 # Ensure there is something

		try:
			if type == "tx":
	#			raise NotImplementedError("Writing items of type 'tx'")
				kds.write(d['txi'][6:].decode('hex_codec'))
				vds.write(d['txv'].decode('hex_codec'))
			elif type == "name":
				kds.write_string(d['hash'])
				vds.write_string(d['name'])
			elif type == "version":
				vds.write_uint32(d['version'])
			elif type == "minversion":
				vds.write_uint32(d['minversion'])
			elif type == "setting":
				raise NotImplementedError("Writing items of type 'setting'")
				kds.write_string(d['setting'])
				#d['value'] = parse_setting(d['setting'], vds)
			elif type == "key":
				kds.write_string(d['public_key'])
				vds.write_string(d['private_key'])
			elif type == "wkey":
				kds.write_string(d['public_key'])
				vds.write_string(d['private_key'])
				vds.write_int64(d['created'])
				vds.write_int64(d['expires'])
				vds.write_string(d['comment'])
			elif type == "defaultkey":
				vds.write_string(d['key'])
			elif type == "pool":
				kds.write_int64(d['n'])
				vds.write_int32(d['nVersion'])
				vds.write_int64(d['nTime'])
				vds.write_string(d['public_key'])
			elif type == "acc":
				kds.write_string(d['account'])
				vds.write_int32(d['nVersion'])
				vds.write_string(d['public_key'])
			elif type == "acentry":
				kds.write_string(d['account'])
				kds.write_uint64(d['n'])
				vds.write_int32(d['nVersion'])
				vds.write_int64(d['nCreditDebit'])
				vds.write_int64(d['nTime'])
				vds.write_string(d['otherAccount'])
				vds.write_string(d['comment'])
			elif type == "bestblock":
				vds.write_int32(d['nVersion'])
				vds.write_compact_size(len(d['hashes']))
				for h in d['hashes']:
					vds.write(h)
			elif type == "ckey":
				kds.write_string(d['public_key'])
				vds.write_string(d['encrypted_private_key'])
			elif type == "mkey":
				kds.write_uint32(d['nID'])
				vds.write_string(d['encrypted_key'])
				vds.write_string(d['salt'])
				vds.write_uint32(d['nDerivationMethod'])
				vds.write_uint32(d['nDerivationIterations'])
				vds.write_string(d['otherParams'])

			else:
				print "Unknown key type: "+type

			# Write the key/value pair to the database
			db.put(kds.input, vds.input)

		except Exception, e:
			print("ERROR writing to wallet.dat, type %s"%type)
			print("data dictionary: %r"%data)
			traceback.print_exc()

def create_new_wallet(db_env, walletfile, version):
	db_out = DB(db_env)

	try:
		r = db_out.open(walletfile, "main", DB_BTREE, DB_CREATE)
	except DBError:
		r = True

	if r is not None:
		logging.error("Couldn't open %s."%walletfile)
		sys.exit(1)

	db_out.put("0776657273696f6e".decode('hex'), ("%08x"%version).decode('hex')[::-1])

	db_out.close()


def rewrite_wallet(db_env, walletfile, destFileName, pre_put_callback=None):
	db = open_wallet(db_env, walletfile)

	db_out = DB(db_env)
	try:
		r = db_out.open(destFileName, "main", DB_BTREE, DB_CREATE)
	except DBError:
		r = True

	if r is not None:
		logging.error("Couldn't open %s."%destFileName)
		sys.exit(1)

	def item_callback(type, d):
		if (pre_put_callback is None or pre_put_callback(type, d)):
			db_out.put(d["__key__"], d["__value__"])

	parse_wallet(db, item_callback)
	db_out.close()
	db.close()

# end of bitcointools wallet.dat handling code

# wallet.dat reader / writer

addr_to_keys={}
def read_wallet(json_db, db_env, walletfile, print_wallet, print_wallet_transactions, transaction_filter, include_balance, vers=-1, FillPool=False):
	global passphrase, addr_to_keys
	crypted=False

	private_keys = []
	private_hex_keys = []

	if vers > -1:
		global addrtype
		oldaddrtype = addrtype
		addrtype = vers

	db = open_wallet(db_env, walletfile, writable=FillPool)

	json_db['keys'] = []
	json_db['pool'] = []
	json_db['tx'] = []
	json_db['names'] = {}
	json_db['ckey'] = []
	json_db['mkey'] = {}

	def item_callback(type, d):
		if type == "tx":
			json_db['tx'].append({"tx_id" : d['tx_id'], "txin" : d['txIn'], "txout" : d['txOut'], "tx_v" : d['txv'], "tx_k" : d['txk']})

		elif type == "name":
			json_db['names'][d['hash']] = d['name']

		elif type == "version":
			json_db['version'] = d['version']

		elif type == "minversion":
			json_db['minversion'] = d['minversion']

		elif type == "setting":
			if not json_db.has_key('settings'): json_db['settings'] = {}
			json_db["settings"][d['setting']] = d['value']

		elif type == "defaultkey":
			json_db['defaultkey'] = public_key_to_bc_address(d['key'])

		elif type == "key":
			addr = public_key_to_bc_address(d['public_key'])
			compressed = d['public_key'][0] != '\04'
			sec = SecretToASecret(PrivKeyToSecret(d['private_key']), compressed)
			hexsec = ASecretToSecret(sec).encode('hex')[:32]
			private_keys.append(sec)
			addr_to_keys[addr]=[hexsec, d['public_key'].encode('hex')]
			json_db['keys'].append({'addr' : addr, 'sec' : sec, 'hexsec' : hexsec, 'secret' : hexsec, 'pubkey':d['public_key'].encode('hex'), 'compressed':compressed, 'private':d['private_key'].encode('hex')})

		elif type == "wkey":
			if not json_db.has_key('wkey'): json_db['wkey'] = []
			json_db['wkey']['created'] = d['created']

		elif type == "pool":
			"	d['n'] = kds.read_int64()
				d['nVersion'] = vds.read_int32()
				d['nTime'] = vds.read_int64()
				d['public_key'] = vds.read_bytes(vds.read_compact_size())"
			try:
				json_db['pool'].append( {'n': d['n'], 'addr': public_key_to_bc_address(d['public_key']), 'addr2': public_key_to_bc_address(d['public_key'].decode('hex')), 'addr3': public_key_to_bc_address(d['public_key'].encode('hex')), 'nTime' : d['nTime'], 'nVersion' : d['nVersion'], 'public_key_hex' : d['public_key'] } )
			except:
				json_db['pool'].append( {'n': d['n'], 'addr': public_key_to_bc_address(d['public_key']), 'nTime' : d['nTime'], 'nVersion' : d['nVersion'], 'public_key_hex' : d['public_key'].encode('hex') } )

		elif type == "acc":
			json_db['acc'] = d['account']
			print("Account %s (current key: %s)"%(d['account'], public_key_to_bc_address(d['public_key'])))

		elif type == "acentry":
			json_db['acentry'] = (d['account'], d['nCreditDebit'], d['otherAccount'], time.ctime(d['nTime']), d['n'], d['comment'])

		elif type == "bestblock":
			json_db['bestblock'] = d['hashes'][0][::-1].encode('hex_codec')

		elif type == "ckey":
			crypted=True
			compressed = d['public_key'][0] != '\04'
			json_db['keys'].append({ 'pubkey': d['public_key'].encode('hex'),'addr': public_key_to_bc_address(d['public_key']), 'encrypted_privkey':  d['encrypted_private_key'].encode('hex_codec'), 'compressed':compressed})

		elif type == "mkey":
			json_db['mkey']['nID'] = d['nID']
			json_db['mkey']['encrypted_key'] = d['encrypted_key'].encode('hex_codec')
			json_db['mkey']['salt'] = d['salt'].encode('hex_codec')
			json_db['mkey']['nDerivationMethod'] = d['nDerivationMethod']
			json_db['mkey']['nDerivationIterations'] = d['nDerivationIterations']
			json_db['mkey']['otherParams'] = d['otherParams']

			if passphrase:
				res = crypter.SetKeyFromPassphrase(passphrase, d['salt'], d['nDerivationIterations'], d['nDerivationMethod'])
				if res == 0:
					logging.error("Unsupported derivation method")
					sys.exit(1)
				masterkey = crypter.Decrypt(d['encrypted_key'])
				crypter.SetKey(masterkey)

		else:
			json_db[type] = 'unsupported'
			print "Wallet data not recognized: "+str(d)

	list_of_reserve_not_in_pool=[]
	parse_wallet(db, item_callback)


	nkeys = len(json_db['keys'])
	i = 0
	for k in json_db['keys']:
		i+=1
		addr = k['addr']
		if include_balance:
#			print("%3d/%d  %s  %s" % (i, nkeys, k["addr"], k["balance"]))
			k["balance"] = balance(balance_site, k["addr"])
#			print("  %s" % (i, nkeys, k["addr"], k["balance"]))

		if addr in json_db['names'].keys():
			k["label"] = json_db['names'][addr]
			k["reserve"] = 0
		else:
			k["reserve"] = 1
			list_of_reserve_not_in_pool.append(k['pubkey'])


	def rnip_callback(a):
		list_of_reserve_not_in_pool.remove(a['public_key_hex'])

	if FillPool:
		map(rnip_callback, json_db['pool'])

		cpt=1
		for p in list_of_reserve_not_in_pool:
			update_wallet(db, 'pool', { 'public_key' : p.decode('hex'), 'n' : cpt, 'nTime' : ts(), 'nVersion':80100 })
			cpt+=1



	db.close()

	crypted = 'salt' in json_db['mkey']

	if not crypted:
		print "The wallet is not encrypted"

	if crypted and not passphrase:
		print "The wallet is encrypted but no passphrase is used"

	if crypted and passphrase:
		check = True
		ppcorrect=True
		for k in json_db['keys']:
		  if 'encrypted_privkey' in k:
			ckey = k['encrypted_privkey'].decode('hex')
			public_key = k['pubkey'].decode('hex')
			crypter.SetIV(Hash(public_key))
			secret = crypter.Decrypt(ckey)
			compressed = public_key[0] != '\04'


			if check:
				check = False
				pkey = EC_KEY(int('0x' + secret.encode('hex'), 16))
				if public_key != GetPubKey(pkey, compressed):
					print "The wallet is encrypted and the passphrase is incorrect"
					ppcorrect=False
					break

			sec = SecretToASecret(secret, compressed)
			k['sec'] = sec
			k['hexsec'] = secret[:32].encode('hex')
			k['secret'] = secret.encode('hex')
			k['compressed'] = compressed
			addr_to_keys[k['addr']]=[sec, k['pubkey']]
#			del(k['ckey'])
#			del(k['secret'])
#			del(k['pubkey'])
			private_keys.append(sec)
		if ppcorrect:
			print "The wallet is encrypted and the passphrase is correct"

	for k in json_db['keys']:
		if k['compressed'] and 'secret' in k:
			k['secret']+="01"

#	del(json_db['pool'])
#	del(json_db['names'])
	if vers > -1:
		addrtype = oldaddrtype

	return {'crypted':crypted}



def importprivkey(db, sec, label, reserve, keyishex, verbose=True, addrv=addrtype):
	if keyishex is None:
		pkey = regenerate_key(sec)
		compressed = is_compressed(sec)
	elif len(sec) == 64:
		pkey = EC_KEY(str_to_long(sec.decode('hex')))
		compressed = False
	elif len(sec) == 66:
		pkey = EC_KEY(str_to_long(sec[:-2].decode('hex')))
		compressed = True
	else:
		print("Hexadecimal private keys must be 64 or 66 characters long (specified one is "+str(len(sec))+" characters long)")
		return False

	if not pkey:
		return False

	secret = GetSecret(pkey)
	private_key = GetPrivKey(pkey, compressed)
	public_key = GetPubKey(pkey, compressed)
	addr = public_key_to_bc_address(public_key, addrv)

	if verbose:
		print "Address (%s): %s"%(aversions[addrv], addr)
		print "Privkey (%s): %s"%(aversions[addrv], SecretToASecret(secret, compressed))
		print "Hexprivkey: %s"%(secret.encode('hex'))
		print "Hash160: %s"%(bc_address_to_hash_160(addr).encode('hex'))
		if not compressed:
			print "Pubkey: 04%.64x%.64x"%(pkey.pubkey.point.x(), pkey.pubkey.point.y())
		else:
			print "Pubkey: 0%d%.64x"%(2+(pkey.pubkey.point.y()&1), pkey.pubkey.point.x())
		if int(secret.encode('hex'), 16)>_r:
			print 'Beware, 0x%s is equivalent to 0x%.33x</b>'%(secret.encode('hex'), int(secret.encode('hex'), 16)-_r)



	global crypter, passphrase, json_db
	crypted = False
	if 'mkey' in json_db.keys() and 'salt' in json_db['mkey']:
		crypted = True
	if crypted:
		if passphrase:
			cry_master = json_db['mkey']['encrypted_key'].decode('hex')
			cry_salt   = json_db['mkey']['salt'].decode('hex')
			cry_rounds = json_db['mkey']['nDerivationIterations']
			cry_method = json_db['mkey']['nDerivationMethod']

			crypter.SetKeyFromPassphrase(passphrase, cry_salt, cry_rounds, cry_method)
#			if verbose:
#				print "Import with", passphrase, "", cry_master.encode('hex'), "", cry_salt.encode('hex')
			masterkey = crypter.Decrypt(cry_master)
			crypter.SetKey(masterkey)
			crypter.SetIV(Hash(public_key))
			e = crypter.Encrypt(secret)
			ck_epk=e

			update_wallet(db, 'ckey', { 'public_key' : public_key, 'encrypted_private_key' : ck_epk })
	else:
		update_wallet(db, 'key', { 'public_key' : public_key, 'private_key' : private_key })

	if not reserve:
		update_wallet(db, 'name', { 'hash' : addr, 'name' : label })


	return True

def balance(site, address):
	page=urllib.urlopen("%s=%s" % (site, address))
	json_acc = json.loads(page.read().split("<end>")[0])
	if json_acc['0'] == 0:
		return "Invalid address"
	elif json_acc['0'] == 2:
		return "Never used"
	else:
		return json_acc['balance']

def read_jsonfile(filename):
	filin = open(filename, 'r')
	txdump = filin.read()
	filin.close()
	return json.loads(txdump)

def write_jsonfile(filename, array):
	filout = open(filename, 'w')
	filout.write(json.dumps(array, sort_keys=True, indent=0))
	filout.close()

def keyinfo(sec, keyishex):
	if keyishex is None:
		pkey = regenerate_key(sec)
		compressed = is_compressed(sec)
	elif len(sec) == 64:
		pkey = EC_KEY(str_to_long(sec.decode('hex')))
		compressed = False
	elif len(sec) == 66:
		pkey = EC_KEY(str_to_long(sec[:-2].decode('hex')))
		compressed = True
	else:
		print("Hexadecimal private keys must be 64 or 66 characters long (specified one is "+str(len(sec))+" characters long)")
		exit(0)

	if not pkey:
		return False

	secret = GetSecret(pkey)
	private_key = GetPrivKey(pkey, compressed)
	public_key = GetPubKey(pkey, compressed)
	addr = public_key_to_bc_address(public_key)

	print "Address (%s): %s" % ( aversions[addrtype], addr )
	print "Privkey (%s): %s" % ( aversions[addrtype], SecretToASecret(secret, compressed) )
	print "Hexprivkey:   %s" % secret.encode('hex')
	print "Hash160:      %s"%(bc_address_to_hash_160(addr).encode('hex'))

	return True


def X_if_else(iftrue, cond, iffalse):
	if cond:
		return iftrue
	return iffalse

def export_all_keys(db, ks, filename):
	txt=";".join(ks)+"\n"
	for i in db['keys']:
	  try:
		j=i.copy()
		if 'label' not in j:
			j['label']='#Reserve'
		t=";".join([str(j[k]) for k in ks])
		txt+=t+"\n"
	  except:
		return False

	try:
		myFile = open(filename, 'w')
		myFile.write(txt)
		myFile.close()
		return True
	except:
		return False

def import_csv_keys(filename, wdir, wname, nbremax=9999999):
	global global_merging_message
	if filename[0]=="\x00":    #yeah, dirty workaround
		content=filename[1:]
	else:
		filen = open(filename, "r")
		content = filen.read()
		filen.close()

	db_env = create_env(wdir)
	read_wallet(json_db, db_env, wname, True, True, "", None)
	db = open_wallet(db_env, wname, writable=True)

	content=content.split('\n')
	content=content[:min(nbremax, len(content))]
	for i in range(len(content)):
	  c=content[i]
	  global_merging_message = ["Merging: "+str(round(100.0*(i+1)/len(content),1))+"%" for j in range(2)]
	  if ';' in c and len(c)>0 and c[0]!="#":
		cs=c.split(';')
		sec,label=cs[0:2]
		v=addrtype
		if len(cs)>2:
			v=int(cs[2])
		reserve=False
		if label=="#Reserve":
			reserve=True
		keyishex=None
		if abs(len(sec)-65)==1:
			keyishex=True
		importprivkey(db, sec, label, reserve, keyishex, verbose=False, addrv=v)

	global_merging_message = ["Merging done.", ""]

	db.close()

	read_wallet(json_db, db_env, wname, True, True, "", None, -1, True)  #Fill the pool if empty

	return True

def message_to_hash(msg, msgIsHex=False):
	str = ""
#	str += '04%064x%064x'%(pubkey.point.x(), pubkey.point.y())
#	str += "Padding text - "
	str += msg
	if msgIsHex:
		str = str.decode('hex')
	hash = Hash(str)
	return hash

def sign_message(secret, msg, msgIsHex=False):
	k = KEY()
	k.generate(secret)
	return k.sign(message_to_hash(msg, msgIsHex))

def verify_message_signature(pubkey, sign, msg, msgIsHex=False):
	k = KEY()
	k.set_pubkey(pubkey.decode('hex'))
	return k.verify(message_to_hash(msg, msgIsHex), sign.decode('hex'))


OP_DUP = 118;
OP_HASH160 = 169;
OP_EQUALVERIFY = 136;
OP_CHECKSIG = 172;

XOP_DUP = "%02x"%OP_DUP;
XOP_HASH160 = "%02x"%OP_HASH160;
XOP_EQUALVERIFY = "%02x"%OP_EQUALVERIFY;
XOP_CHECKSIG = "%02x"%OP_CHECKSIG;

BTC = 1e8

def ct(l_prevh, l_prevn, l_prevsig, l_prevpubkey, l_value_out, l_pubkey_out, is_msg_to_sign=-1, oldScriptPubkey=""):
	scriptSig = True
	if is_msg_to_sign is not -1:
		scriptSig = False
		index = is_msg_to_sign

	ret = ""
	ret += inverse_str("%08x"%1)
	nvin = len(l_prevh)
	ret += "%02x"%nvin

	for i in range(nvin):
		txin_ret = ""
		txin_ret2 = ""

		txin_ret += inverse_str(l_prevh[i])
		txin_ret += inverse_str("%08x"%l_prevn[i])

		if scriptSig:
			txin_ret2 += "%02x"%(1+len(l_prevsig[i])/2)
			txin_ret2 += l_prevsig[i]
			txin_ret2 += "01"
			txin_ret2 += "%02x"%(len(l_prevpubkey[i])/2)
			txin_ret2 += l_prevpubkey[i]

			txin_ret += "%02x"%(len(txin_ret2)/2)
			txin_ret += txin_ret2

		elif index == i:
			txin_ret += "%02x"%(len(oldScriptPubkey)/2)
			txin_ret += oldScriptPubkey
		else:
			txin_ret += "00"

		ret += txin_ret
		ret += "ffffffff"


	nvout = len(l_value_out)
	ret += "%02x"%nvout
	for i in range(nvout):
		txout_ret = ""

		txout_ret += inverse_str("%016x"%(l_value_out[i]))
		txout_ret += "%02x"%(len(l_pubkey_out[i])/2+5)
		txout_ret += "%02x"%OP_DUP
		txout_ret += "%02x"%OP_HASH160
		txout_ret += "%02x"%(len(l_pubkey_out[i])/2)
		txout_ret += l_pubkey_out[i]
		txout_ret += "%02x"%OP_EQUALVERIFY
		txout_ret += "%02x"%OP_CHECKSIG
		ret += txout_ret

	ret += "00000000"
	if not scriptSig:
		ret += "01000000"
	return ret

def create_transaction(secret_key, hashes_txin, indexes_txin, pubkey_txin, prevScriptPubKey, amounts_txout, scriptPubkey):
	li1 = len(secret_key)
	li2 = len(hashes_txin)
	li3 = len(indexes_txin)
	li4 = len(pubkey_txin)
	li5 = len(prevScriptPubKey)

	if li1 != li2 or li2 != li3 or li3 != li4 or li4 != li5:
		print("Error in the number of tx inputs")
		exit(0)

	lo1 = len(amounts_txout)
	lo2 = len(scriptPubkey)

	if lo1 != lo2:
		print("Error in the number of tx outputs")
		exit(0)

	sig_txin = []
	i=0
	for cpt in hashes_txin:
		sig_txin.append(sign_message(secret_key[i].decode('hex'), ct(hashes_txin, indexes_txin, sig_txin, pubkey_txin, amounts_txout, scriptPubkey, i, prevScriptPubKey[i]), True)+"01")
		i+=1

	tx = ct(hashes_txin, indexes_txin, sig_txin, pubkey_txin, amounts_txout, scriptPubkey)
	hashtx = Hash(tx.decode('hex')).encode('hex')

	for i in range(len(sig_txin)):
		try:
			verify_message_signature(pubkey_txin[i], sig_txin[i][:-2], ct(hashes_txin, indexes_txin, sig_txin, pubkey_txin, amounts_txout, scriptPubkey, i, prevScriptPubKey[i]), True)
			print("sig %2d: verif ok"%i)
		except:
			print("sig %2d: verif error"%i)
			exit(0)

#	tx += end_of_wallettx([], int(time.time()))
#	return [inverse_str(hashtx), "027478" + hashtx, tx]
	return [inverse_str(hashtx), "", tx]

def inverse_str(string):
	ret = ""
	for i in range(len(string)/2):
		ret += string[len(string)-2-2*i];
		ret += string[len(string)-2-2*i+1];
	return ret

def read_table(table, beg, end):
	rows = table.split(beg)
	for i in range(len(rows)):
		rows[i] = rows[i].split(end)[0]
	return rows

def read_blockexplorer_table(table):
	cell = []
	rows = read_table(table, '<tr>', '</tr>')
	for i in range(len(rows)):
		cell.append(read_table(rows[i], '<td>', '</td>'))
		del cell[i][0]
	del cell[0]
	del cell[0]
	return cell

txin_amounts = {}

def bc_address_to_available_tx(address, testnet=False):
	TN=""
	if testnet:
		TN="testnet"

	blockexplorer_url = "http://blockexplorer.com/"+TN+"/address/"
	ret = ""
	txin = []
	txin_no = {}
	global txin_amounts
	txout = []
	balance = 0
	txin_is_used = {}

	page = urllib.urlopen("%s/%s" % (blockexplorer_url, address))
	try:
		table = page.read().split('<table class="txtable">')[1]
		table = table.split("</table>")[0]
	except:
		return {address:[]}

	cell = read_blockexplorer_table(table)

	for i in range(len(cell)):
		txhash = read_table(cell[i][0], '/tx/', '#')[1]
		post_hash = read_table(cell[i][0], '#', '">')[1]
		io = post_hash[0]
		no_tx = post_hash[1:]
		if io in 'i':
			txout.append([txhash, post_hash])
		else:
			txin.append(txhash+no_tx)
			txin_no[txhash+no_tx] = post_hash[1:]
			txin_is_used[txhash+no_tx] = 0

		#hashblock = read_table(cell[i][1], '/block/', '">')[1]
		#blocknumber = read_table(cell[i][1], 'Block ', '</a>')[1]

		txin_amounts[txhash+no_tx] = round(float(cell[i][2]), 8)

#		if cell[i][3][:4] in 'Sent' and io in 'o':
#			print(cell[i][3][:4])
#			print(io)
#			return 'error'
#		if cell[i][3][:4] in 'Rece' and io in 'i':
#			print(cell[i][3][:4])
#			print(io)
#			return 'error'

		balance = round(float(cell[i][5]), 8)


	for tx in txout:
		pagetx = urllib.urlopen("http://blockexplorer.com/"+TN+"/tx/"+tx[0])
		table_in = pagetx.read().split('<a name="outputs">Outputs</a>')[0].split('<table class="txtable">')[1].split("</table>")[0]

		cell = read_blockexplorer_table(table_in)
		for i in range(len(cell)):
			txhash = read_table(cell[i][0], '/tx/', '#')[1]
			no_tx = read_table(cell[i][0], '#', '">')[1][1:]

			if txhash+no_tx in txin:
				txin_is_used[txhash+no_tx] = 1

	ret = []
	for tx in txin:
		if not txin_is_used[tx]:
			ret.append([tx,txin_amounts[tx],txin_no[tx]])

	return {address : ret}

ct_txin = []
ct_txout = []


empty_txin={'hash':'', 'index':'', 'sig':'##', 'pubkey':'', 'oldscript':'', 'addr':''}
empty_txout={'amount':'', 'script':''}

class tx():
	ins=[]
	outs=[]
	tosign=False

	def hashtypeone(index,script):
		global empty_txin
		for i in range(len(ins)):
			self.ins[i]=empty_txin
		self.ins[index]['pubkey']=""
		self.ins[index]['oldscript']=s
		self.tosign=True

	def copy():
		r=tx()
		r.ins=self.ins[:]
		r.outs=self.outs[:]
		return r

	def sign(n=-1):
		if n==-1:
			for i in range(len(ins)):
				self.sign(i)
				return "done"

		global json_db
		txcopy=self.copy()
		txcopy.hashtypeone(i, self.ins[n]['oldscript'])

		sec=''
		for k in json_db['keys']:
		  if k['addr']==self.ins[n]['addr'] and 'hexsec' in k:
			sec=k['hexsec']
		if sec=='':
			print "priv key not found (addr:"+self.ins[n]['addr']+")"
			return ""

		self.ins[n]['sig']=sign_message(sec.decode('hex'), txcopy.get_tx(), True)

	def ser():
		r={}
		r['ins']=self.ins
		r['outs']=self.outs
		r['tosign']=self.tosign
		return json.dumps(r)

	def unser(r):
		s=json.loads(r)
		self.ins=s['ins']
		self.outs=s['outs']
		self.tosign=s['tosign']

	def get_tx():
		r=''
		ret += inverse_str("%08x"%1)
		ret += "%02x"%len(self.ins)

		for i in range(len(self.ins)):
			txin=self.ins[i]
			ret += inverse_str(txin['hash'])
			ret += inverse_str("%08x"%txin['index'])

			if txin['pubkey']!="":
				tmp += "%02x"%(1+len(txin['sig'])/2)
				tmp += txin['sig']
				tmp += "01"
				tmp += "%02x"%(len(txin['pubkey'])/2)
				tmp += txin['pubkey']

				ret += "%02x"%(len(tmp)/2)
				ret += tmp

			elif txin['oldscript']!="":
				ret += "%02x"%(len(txin['oldscript'])/2)
				ret += txin['oldscript']

			else:
				ret += "00"

			ret += "ffffffff"

		ret += "%02x"%len(self.outs)

		for i in range(len(self.outs)):
			txout=self.outs[i]
			ret += inverse_str("%016x"%(txout['amount']))

			if txout['script'][:2]=='s:':  #script
				script=txout['script'][:2]
				ret += "%02x"%(len(script)/2)
				ret += script
			else:                         #address
				ret += "%02x"%(len(txout['script'])/2+5)
				ret += "%02x"%OP_DUP
				ret += "%02x"%OP_HASH160
				ret += "%02x"%(len(txout['script'])/2)
				ret += txout['script']
				ret += "%02x"%OP_EQUALVERIFY
				ret += "%02x"%OP_CHECKSIG

		ret += "00000000"
		if not self.tosign:
			ret += "01000000"
		return ret

def update_pyw():
	if md5_last_pywallet[0] and md5_last_pywallet[1] not in md5_pywallet:
		dl=urllib.urlopen('https://raw.github.com/jackjack-jj/pywallet/master/pywallet.py').read()
		if len(dl)>40 and md5_2(dl)==md5_last_pywallet[1]:
			filout = open(pyw_path+"/"+pyw_filename, 'w')
			filout.write(dl)
			filout.close()
			thread.start_new_thread(restart_pywallet, ())
			return "Updated, restarting..."
		else:
			return "Problem when downloading new version ("+md5_2(dl)+"/"+md5_last_pywallet[1]+")"

def restart_pywallet():
	thread.start_new_thread(start_pywallet, ())
	time.sleep(2)
	reactor.stop()

def start_pywallet():
	a=Popen("python "+pyw_path+"/"+pyw_filename+" --web --port "+str(webport)+" --wait 3", shell=True, bufsize=-1, stdout=PIPE).stdout
	a.close()

def clone_wallet(parentPath, clonePath):
	types,datas=[],[]
	parentdir,parentname=os.path.split(parentPath)
	wdir,wname=os.path.split(clonePath)

	db_env = create_env(parentdir)
	read_wallet(json_db, db_env, parentname, True, True, "", False)

	types.append('version')
	datas.append({'version':json_db['version']})
	types.append('defaultkey')
	datas.append({'key':json_db['defaultkey']})
	for k in json_db['keys']:
		types.append('ckey')
		datas.append({'public_key':k['pubkey'].decode('hex'),'encrypted_private_key':random_string(96).decode('hex')})
	for k in json_db['pool']:
		types.append('pool')
		datas.append({'n':k['n'],'nVersion':k['nVersion'],'nTime':k['nTime'],'public_key':k['public_key_hex'].decode('hex')})
	for addr,label in json_db['names'].items():
		types.append('name')
		datas.append({'hash':addr,'name':'Watch:'+label})

	db_env = create_env(wdir)
	create_new_wallet(db_env, wname, 60000)

	db = open_wallet(db_env, wname, True)
	NPP_salt=random_string(16).decode('hex')
	NPP_rounds=int(50000+random.random()*20000)
	NPP_method=0
	NPP_MK=random_string(64).decode('hex')
	crypter.SetKeyFromPassphrase(random_string(64), NPP_salt, NPP_rounds, NPP_method)
	NPP_EMK = crypter.Encrypt(NPP_MK)
	update_wallet(db, 'mkey', {
		"encrypted_key": NPP_EMK,
		'nDerivationIterations' : NPP_rounds,
		'nDerivationMethod' : NPP_method,
		'nID' : 1,
		'otherParams' : ''.decode('hex'),
		"salt": NPP_salt
	})
	db.close()

	read_wallet(json_db, db_env, wname, True, True, "", False)

	db = open_wallet(db_env, wname, writable=True)
	update_wallet(db, types, datas, True)
	db.close()
	print "Wallet successfully cloned to:\n   %s"%clonePath

import thread
md5_last_pywallet = [False, ""]

def retrieve_last_pywallet_md5():
	global md5_last_pywallet
	md5_last_pywallet = [True, md5_onlinefile('https://raw.github.com/jackjack-jj/pywallet/master/pywallet.py')]

from optparse import OptionParser

if __name__ == '__main__':
	parser = OptionParser(usage="%prog [options]", version="%prog 1.1")

	parser.add_option("--passphrase", dest="passphrase",
		help="passphrase for the encrypted wallet")

	parser.add_option("--dumpwallet", dest="dump", action="store_true",
		help="dump wallet in json format")

	parser.add_option("--dumpwithbalance", dest="dumpbalance", action="store_true",
		help="includes balance of each address in the json dump, takes about 2 minutes per 100 addresses")

	parser.add_option("--importprivkey", dest="key",
		help="import private key from vanitygen")

	parser.add_option("--importhex", dest="keyishex", action="store_true",
		help="KEY is in hexadecimal format")

	parser.add_option("--datadir", dest="datadir",
		help="wallet directory (defaults to bitcoin default)")

	parser.add_option("--wallet", dest="walletfile",
		help="wallet filename (defaults to wallet.dat)",
		default="wallet.dat")

	parser.add_option("--label", dest="label",
		help="label shown in the adress book (defaults to '')",
		default="")

	parser.add_option("--testnet", dest="testnet", action="store_true",
		help="use testnet subdirectory and address type")

	parser.add_option("--namecoin", dest="namecoin", action="store_true",
		help="use namecoin address type")

	parser.add_option("--otherversion", dest="otherversion",
		help="use other network address type, whose version is OTHERVERSION")

	parser.add_option("--info", dest="keyinfo", action="store_true",
		help="display pubkey, privkey (both depending on the network) and hexkey")

	parser.add_option("--reserve", dest="reserve", action="store_true",
		help="import as a reserve key, i.e. it won't show in the adress book")

	parser.add_option("--multidelete", dest="multidelete",
		help="deletes data in your wallet, according to the file provided")

	parser.add_option("--balance", dest="key_balance",
		help="prints balance of KEY_BALANCE")

	parser.add_option("--web", dest="web", action="store_true",
		help="run pywallet web interface")

	parser.add_option("--port", dest="port",
		help="port of web interface (defaults to 8989)")

	parser.add_option("--recover", dest="recover", action="store_true",
		help="recover your deleted keys, use with recov_size and recov_device")

	parser.add_option("--recov_device", dest="recov_device",
		help="device to read (e.g. /dev/sda1 or E: or a file)")

	parser.add_option("--recov_size", dest="recov_size",
		help="number of bytes to read (e.g. 20Mo or 50Gio)")

	parser.add_option("--recov_outputdir", dest="recov_outputdir",
		help="output directory where the recovered wallet will be put")

	parser.add_option("--clone_watchonly_from", dest="clone_watchonly_from",
		help="path of the original wallet")

	parser.add_option("--clone_watchonly_to", dest="clone_watchonly_to",
		help="path of the resulting watch-only wallet")

	parser.add_option("--dont_check_walletversion", dest="dcv", action="store_true",
		help="don't check if wallet version > %d before running (WARNING: this may break your wallet, be sure you know what you do)"%max_version)

	parser.add_option("--wait", dest="nseconds",
		help="wait NSECONDS seconds before launch")


#	parser.add_option("--forcerun", dest="forcerun",
#		action="store_true",
#		help="run even if pywallet detects bitcoin is running")

	(options, args) = parser.parse_args()

#	a=Popen("ps xa | grep ' bitcoin'", shell=True, bufsize=-1, stdout=PIPE).stdout
#	aread=a.read()
#	nl = aread.count("\n")
#	a.close()
#	if nl > 2:
#		print('Bitcoin seems to be running: \n"%s"'%(aread))
#		if options.forcerun is None:
#			exit(0)

	if options.nseconds:
		time.sleep(int(options.nseconds))

	if options.passphrase:
		passphrase = options.passphrase

	if options.clone_watchonly_from is not None and options.clone_watchonly_to:
		clone_wallet(options.clone_watchonly_from, options.clone_watchonly_to)
		exit(0)


	if options.recover:
		if options.recov_size is None or options.recov_device is None or options.recov_outputdir is None:
			print("You must provide the device, the number of bytes to read and the output directory")
			exit(0)
		device = options.recov_device
		if len(device) in [2,3] and device[1]==':':
			device="\\\\.\\"+device
		size = read_device_size(options.recov_size)

		passphraseRecov=''
		while passphraseRecov=='':
			passphraseRecov=raw_input("Enter the passphrase for the wallet that will contain all the recovered keys: ")
		passphrase=passphraseRecov

		passes=[]
		p=' '
		print '\nEnter the possible passphrases used in your deleted wallets.'
		print "Don't forget that more passphrases = more time to test the possibilities."
		print 'Write one passphrase per line and end with an empty line.'
		while p!='':
			p=raw_input("Possible passphrase: ")
			if p!='':
				passes.append(p)

		print "\nStarting recovery."
		recoveredKeys=recov(device, passes, size, 10240, options.recov_outputdir)
		recoveredKeys=list(set(recoveredKeys))
#		print recoveredKeys[0:5]


		db_env = create_env(options.recov_outputdir)
		recov_wallet_name = "recovered_wallet_%s.dat"%ts()

		create_new_wallet(db_env, recov_wallet_name, 32500)

		if passphraseRecov!="I don't want to put a password on the recovered wallet and I know what can be the consequences.":
			db = open_wallet(db_env, recov_wallet_name, True)

			NPP_salt=random_string(16).decode('hex')
			NPP_rounds=int(50000+random.random()*20000)
			NPP_method=0
			NPP_MK=random_string(64).decode('hex')
			crypter.SetKeyFromPassphrase(passphraseRecov, NPP_salt, NPP_rounds, NPP_method)
			NPP_EMK = crypter.Encrypt(NPP_MK)
			update_wallet(db, 'mkey', {
				"encrypted_key": NPP_EMK,
				'nDerivationIterations' : NPP_rounds,
				'nDerivationMethod' : NPP_method,
				'nID' : 1,
				'otherParams' : ''.decode('hex'),
				"salt": NPP_salt
			})
			db.close()

		read_wallet(json_db, db_env, recov_wallet_name, True, True, "", False)

		db = open_wallet(db_env, recov_wallet_name, True)

		print "\n\nImporting:"
		for i,sec in enumerate(recoveredKeys):
			sec=sec.encode('hex')
			print("\nImporting key %4d/%d:"%(i+1, len(recoveredKeys)))
			importprivkey(db, sec, "recovered: %s"%sec, None, True)
		db.close()

		print("\n\nThe new wallet %s/%s contains the %d recovered key%s"%(options.recov_outputdir, recov_wallet_name, len(recoveredKeys), iais(len(recoveredKeys))))

		exit(0)


	if 'bsddb' in missing_dep:
		print("pywallet needs 'bsddb' package to run, please install it")
		exit(0)

	if 'ecdsa' in missing_dep:
		print("'ecdsa' package is not installed, pywallet won't be able to sign/verify messages")

			importprivkey(db, sec+'01', "recovered: %s"%sec, None, True)
	if options.dcv is not None:
		max_version = 10 ** 9

	if options.datadir is not None:
		wallet_dir = options.datadir

	if options.walletfile is not None:
		wallet_name = options.walletfile

	if 'twisted' not in missing_dep and options.web is not None:
		md5_pywallet = md5_file(pyw_path+"/"+pyw_filename)
		thread.start_new_thread(retrieve_last_pywallet_md5, ())

		webport = 8989
		if options.port is not None:
			webport = int(options.port)
		root = WIRoot()
		for viewName, className in VIEWS.items():
			root.putChild(viewName, className)
		log.startLogging(sys.stdout)
		log.msg('Starting server: %s' %str(datetime.now()))
		server = server.Site(root)
		reactor.listenTCP(webport, server)
		reactor.run()
		exit(0)

	if options.key_balance is not None:
		print(balance(balance_site, options.key_balance))
		exit(0)

	if options.dump is None and options.key is None and options.multidelete is None:
		print "A mandatory option is missing\n"
		parser.print_help()
		exit(0)

	if options.testnet:
		db_dir += "/testnet"
		addrtype = 111

	if options.namecoin or options.otherversion is not None:
		if options.datadir is None and options.keyinfo is None:
			print("You must provide your wallet directory")
			exit(0)
		else:
			if options.namecoin:
				addrtype = 52
			else:
				addrtype = int(options.otherversion)

	if options.keyinfo is not None:
		if not keyinfo(options.key, options.keyishex):
			print "Bad private key"
		exit(0)

	db_dir = determine_db_dir()

	db_env = create_env(db_dir)

	if options.multidelete is not None:
		filename=options.multidelete
		filin = open(filename, 'r')
		content = filin.read().split('\n')
		filin.close()
		typedel=content[0]
		kd=filter(bool,content[1:])
		try:
			r=delete_from_wallet(db_env, determine_db_name(), typedel, kd)
			print '%d element%s deleted'%(r, 's'*(int(r>1)))
		except:
			print "Error: do not try to delete a non-existing transaction."
			exit(1)
		exit(0)


	read_wallet(json_db, db_env, determine_db_name(), True, True, "", options.dumpbalance is not None)

	if json_db.get('minversion') > max_version:
		print "Version mismatch (must be <= %d)" % max_version
		#exit(1)

	if options.dump:
		print json.dumps(json_db, sort_keys=True, indent=4)
	elif options.key:
		if json_db['version'] > max_version:
			print "Version mismatch (must be <= %d)" % max_version
		elif (options.keyishex is None and options.key in private_keys) or (options.keyishex is not None and options.key in private_hex_keys):
			print "Already exists"
		else:
			db = open_wallet(db_env, determine_db_name(), writable=True)

			if importprivkey(db, options.key, options.label, options.reserve, options.keyishex):
				print "Imported successfully"
			else:
				print "Bad private key"

			db.close()
"""

from pickle import dumps, loads

# wallet variables and initialization
wallet_dir = os.path.expanduser("~/.bitcoinpy")
wallet_name = "wallet.dat"

# wallet functions
def create_env(db_dir):
	db_env = DBEnv(0)
	r = db_env.open(db_dir, (DB_CREATE|DB_INIT_LOCK|DB_INIT_LOG|DB_INIT_MPOOL|DB_INIT_TXN|DB_THREAD|DB_RECOVER))
	return db_env
	
def open_wallet(db_env, walletfile, writable=False):
	db = DB(db_env)
	if writable:
		DB_TYPEOPEN = DB_CREATE
	else:
		DB_TYPEOPEN = DB_RDONLY
	flags = DB_THREAD | DB_TYPEOPEN
	try:
		r = db.open(walletfile, "main", DB_BTREE, flags)
	except DBError:
		r = True

	if r is not None:
		logging.error("Couldn't open wallet.dat/main. Try quitting Bitcoin and running this again.")
		sys.exit(1)

	return db

# Joric/bitcoin-dev, june 2012, public domain

import hashlib
import ctypes
import ctypes.util
import sys

ssl = ctypes.cdll.LoadLibrary (ctypes.util.find_library ('ssl') or 'libeay32')

def check_result (val, func, args):
    if val == 0: raise ValueError 
    else: return ctypes.c_void_p (val)

ssl.EC_KEY_new_by_curve_name.restype = ctypes.c_void_p
ssl.EC_KEY_new_by_curve_name.errcheck = check_result

class KEY:
    def __init__(self):
        NID_secp256k1 = 714
        self.k = ssl.EC_KEY_new_by_curve_name(NID_secp256k1)
        self.compressed = False
        self.POINT_CONVERSION_COMPRESSED = 2
        self.POINT_CONVERSION_UNCOMPRESSED = 4

    def __del__(self):
        if ssl:
            ssl.EC_KEY_free(self.k)
        self.k = None

    def generate(self, secret=None):
        if secret:
            self.prikey = secret
            priv_key = ssl.BN_bin2bn(secret, 32, ssl.BN_new())
            group = ssl.EC_KEY_get0_group(self.k)
            pub_key = ssl.EC_POINT_new(group)
            ctx = ssl.BN_CTX_new()
            ssl.EC_POINT_mul(group, pub_key, priv_key, None, None, ctx)
            ssl.EC_KEY_set_private_key(self.k, priv_key)
            ssl.EC_KEY_set_public_key(self.k, pub_key)
            ssl.EC_POINT_free(pub_key)
            ssl.BN_CTX_free(ctx)
            return self.k
        else:
            return ssl.EC_KEY_generate_key(self.k)

    def get_pubkey(self):
        size = ssl.i2o_ECPublicKey(self.k, 0)
        mb = ctypes.create_string_buffer(size)
        ssl.i2o_ECPublicKey(self.k, ctypes.byref(ctypes.pointer(mb)))
        return mb.raw

    def get_secret(self):
        bn = ssl.EC_KEY_get0_private_key(self.k);
        bytes = (ssl.BN_num_bits(bn) + 7) / 8
        mb = ctypes.create_string_buffer(bytes)
        n = ssl.BN_bn2bin(bn, mb);
        return mb.raw.rjust(32, chr(0))

    def set_compressed(self, compressed):
        self.compressed = compressed
        if compressed:
            form = self.POINT_CONVERSION_COMPRESSED
        else:
            form = self.POINT_CONVERSION_UNCOMPRESSED
        ssl.EC_KEY_set_conv_form(self.k, form)

def dhash(s):
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()

def rhash(s):
    h1 = hashlib.new('ripemd160')
    h1.update(hashlib.sha256(s).digest())
    return h1.digest()

b58_digits = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def base58_encode(n):
    l = []
    while n > 0:
        n, r = divmod(n, 58)
        l.insert(0,(b58_digits[r]))
    return ''.join(l)

def base58_decode(s):
    n = 0
    for ch in s:
        n *= 58
        digit = b58_digits.index(ch)
        n += digit
    return n

def base58_encode_padded(s):
    res = base58_encode(int('0x' + s.encode('hex'), 16))
    pad = 0
    for c in s:
        if c == chr(0):
            pad += 1
        else:
            break
    return b58_digits[0] * pad + res

def base58_decode_padded(s):
    pad = 0
    for c in s:
        if c == b58_digits[0]:
            pad += 1
        else:
            break
    h = '%x' % base58_decode(s)
    if len(h) % 2:
        h = '0' + h
    res = h.decode('hex')
    return chr(0) * pad + res

def base58_check_encode(s, version=0):
    vs = chr(version) + s
    check = dhash(vs)[:4]
    return base58_encode_padded(vs + check)

def base58_check_decode(s, version=0):
    k = base58_decode_padded(s)
    v0, data, check0 = k[0], k[1:-4], k[-4:]
    check1 = dhash(v0 + data)[:4]
    if check0 != check1:
        raise BaseException('checksum error')
    if version != ord(v0):
        raise BaseException('version mismatch')
    return data

def gen_eckey(passphrase=None, secret=None, pkey=None, compressed=False, rounds=1, version=0):
    k = KEY()
    if passphrase:
        secret = passphrase.encode('utf8')
        for i in xrange(rounds):
            secret = hashlib.sha256(secret).digest()
    if pkey:
        secret = base58_check_decode(pkey, 128+version)
        compressed = len(secret) == 33
        secret = secret[0:32]
    k.generate(secret)
    k.set_compressed(compressed)
    return k

def get_addr(k,version=0):
    pubkey = k.get_pubkey()
    secret = k.get_secret()
    hash160 = rhash(pubkey)
    addr = base58_check_encode(hash160,version)
    payload = secret
    if k.compressed:
        payload = secret + chr(1)
    pkey = base58_check_encode(payload, 128+version)
    return addr, pkey

def reencode(pkey,version=0):
    payload = base58_check_decode(pkey,128+version)
    secret = payload[:-1]
    payload = secret + chr(1)
    pkey = base58_check_encode(payload, 128+version)
    print get_addr(gen_eckey(pkey))

# interface functions
def getnewaddress():
    key = gen_eckey()
    address, private_key = get_addr(key)
    return address

def scan_block(index, address):
    return 1.0

def getbalance(account):
    walletdb = open_wallet(db_env, walletfile, writable = True)
    # get account
    accountinfo = loads(walletdb[account])
    public_key = accountinfo['public_key']
    private_key = accountinfo['private_key']
    address = accountinfo['address']
    balance = accountinfo['balance']
    height = accountinfo['height']
    
    print "\t Public key: ", public_key
    print "\tPrivate key: ", private_key
    print "\tAddress: ", address
    print "\tBalance: ", balance

    # get chaindb from bitcoinpy
    balance = chaindb.getbalance(address)
    walletdb[account] = dumps({"public_key": "Public key", "private_key": private_key, "address": address, "balance": balance, "height" : height})
    walletdb.close()
    
    return balance

def sendtoaddress(address, amount):
    print "sent :", amount, " to address: ", address
    return True

def init_wallet(walletfile):
    walletdb = open_wallet(db_env, walletfile, writable = True)
    # if wallet is already initialized, skip initilazation
    if 'accounts' not in walletdb:
        print "Initilizing wallet"
        walletdb['accounts'] = dumps(['account', 'account1'])
        key = gen_eckey()
        address, private_key = get_addr(key)
        walletdb['account'] = dumps({"public_key": "Public key", "private_key": private_key, "address": address, "balance": 0.0, "height" : 0})
        walletdb.sync()
    walletdb.close()

# initilization functions
db_env = create_env(wallet_dir)
walletfile = os.path.join(wallet_dir, wallet_name)
walletdb = None
init_wallet(walletfile)
