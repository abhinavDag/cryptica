from cachetools import TTLCache
import globals
from Block import Block
import script

# this class contains information about the nodes present in the network, ie other users
class Nodes:
    def __init__(self, wallet, miner):

        # list of all the usernames of discovered hosts
        self.usernames_to_public_keys = {
            wallet.username : wallet.key.public_key().export_key()
        }


        # stores the known balances of the nodes that are discovered
        self.balances = {
            wallet.key.public_key().export_key(): wallet.balance   
        }

        # stores ips from which messages are received
        self.ip_addresses = [globals.OWN_IP]

        # here we are creating the genesis_block for the block_chain
        # it is nothing but an empty block containing no information
        # except the block_hash
        genesis_block = Block()
        genesis_block_json = genesis_block.to_json()
        nonce = miner.nonce_generator(genesis_block_json, globals.GENESIS_BLOCK_LEADING_ZEROES)
        genesis_block.block_hash = script.sha256_bits_str(genesis_block_json+str(nonce))
        genesis_block.nonce = nonce

        # this is the block chain itself, an array of Block objects
        self.block_chain = [genesis_block]
        
        # below, we are going to create a cache for transactions.
        # it will store the signatures of the transactions.
        # ttl is in seconds, maxsize defines the maximum size of the cache
        self.transaction_signature_cache = TTLCache(maxsize=100, ttl=globals.TRANSACTION_CACHE_TTL)
