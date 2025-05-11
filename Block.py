import json
from Transaction import Transaction
import script

# class defining each block of the blockchain
class Block:
    def __init__(self, previous_block_hash=None, transactions_list=None):
        self.previous_block_hash = previous_block_hash
        self.transactions_list = transactions_list
        self.nonce = 0
        self.block_hash = ""
        
    # creates a json of itself
    def to_json(self):
        json_transactions_list = []
        if(self.transactions_list):
            for transaction in self.transactions_list:
                transaction_json = transaction.to_json()
                json_transactions_list.append(transaction_json)

        block_dict =  {
            "previous_block_hash": self.previous_block_hash,
            "transactions_list": json_transactions_list,
            "nonce": self.nonce,
            "block_hash": self.block_hash
        }
        block_json = json.dumps(block_dict)
        return block_json

    # creates a block object from the json provided
    def from_json(self, block_json):
        block_dict = json.loads(block_json)
        self.previous_block_hash = block_dict['previous_block_hash']
        json_transactions_list = block_dict['transactions_list']
        transactions_list = []
        for transaction_json in json_transactions_list:
            transaction = Transaction()
            transaction.from_json(transaction_json)
            transactions_list.append(transaction)

        self.transactions_list = transactions_list
        self.nonce = block_dict['nonce']
        self.block_hash = block_dict['block_hash']

    def is_valid(self):
        
        # what we check here is the following, upon concatinating the
        # given nonce to the block json and hashing, we get the block_hash
        dup_block_object = self
        dup_block_object.nonce = 0
        dup_block_object.block_hash = ""
        block_json = dup_block_object.to_json()
        return script.sha256_bits_str(block_json + str(self.nonce)) == self.block_hash
        
