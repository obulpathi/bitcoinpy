import utils
import binascii

address = "16UwLL9Risc3QfPqBUvKofHmBQ7wMtjvM"
public_key_hex = "0450863AD64A87AE8A2FE83C1AF1A8403CB53F53E486D8511DAD8A04887E5B23522CD470243453A299FA9E77237716103ABC11A1DF38855ED6F2EE187E9C582BA6"
private_key_hex = "18E14A7B6A307F426A94F8114701E7C8E774E7F9A47E2C2035DB29A206321725"
public_key_hash = "010966776006953D5567439E5E39F86A0D273BEE"

print "public key hex: ", public_key_hex
print "public_key_hash: ", public_key_hash
print "private key hex: ", private_key_hex
print "address: ", address

#print "Public key hex to address:" , utils.public_key_hex_to_address(public_key_hex)
print "address_to_public_key_hash: ", binascii.hexlify(utils.address_to_public_key_hash(address))
#print "public key hash: ", public_key_hash
