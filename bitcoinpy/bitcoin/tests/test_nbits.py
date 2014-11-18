import binascii
from bitcoin.serialize import *

compact = 0x1b00ffff
print "seed compact: ", hex(compact)
target = uint256_from_compact(compact)
print "target: ", hex(target)
compact = compact_from_uint256(target)
print "compact: ", hex(compact)

