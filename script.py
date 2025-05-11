from Crypto.Hash import SHA256

# takes non encoded data and gives you sha256 in string of bits
def sha256_bits_str(data):
    hash = SHA256.new(data.encode())
    hash_bit_string = bin(int(hash.hexdigest(), 16))[2:].zfill(256)
    return hash_bit_string

# return True if hash has enough leading zeroes, False otherwise 
def valid_block_hash(hash_bits_str, leading_zeroes):
    for i in range(leading_zeroes):
        if(hash_bits_str[i] != "0"):
            return False
    return True
