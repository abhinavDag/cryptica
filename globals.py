import socket

# own ip of the machine
OWN_IP = socket.gethostbyname(socket.gethostname())

# the broadcast ip for the network
BROADCAST_IP = "255.255.255.255"

# all interface listen ip
LISTEN_IP = "0.0.0.0"

# broadcast port, listen and send
BROADCAST_PORT = 5050

# size of the header of the broadcast message
HEADER = 48

# total size of the broadcast message
MESSAGE_SIZE = 4096

# how many leading zeroes for the hash to be right
LEADING_ZEROES = 20

# this tells us how many leading zeroes should the
# genesis block contain, because, genesis block mining
# should not be hard, and be the same for all
GENESIS_BLOCK_LEADING_ZEROES = 2

# this is how many seconds the ttl of a transaction sign in cache is
TRANSACTION_CACHE_TTL = 3600

# this is how many seconds from time of initialization the
# transaction is treated is valid for
TRANSACTION_EXPIRATION = 3600

# this constant tells us the block reward, ie the reward
# that we get for mining a block
BLOCK_REWARD = 50
