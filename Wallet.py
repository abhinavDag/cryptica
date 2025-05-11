from json.encoder import encode_basestring
from Crypto.PublicKey import RSA
from Block import Block
import globals
from Transaction import Transaction
import json
import ErrorMessages
from Nodes import Nodes
import time
from P2P import P2P
import state_vars
import script
from base64 import b64encode, b64decode
from Miner import Miner

# this class contains everything about transactions and wallet balances, each person gets one wallet
class Wallet:
    def __init__(self, username):
    
        self.key = RSA.generate(2048)
        self.username = username
        self.wallet_nonce = 0
        self.balance = 0
        self.miner = Miner()
        self.nodes = Nodes(self, self.miner)
        self.p2p = P2P()

    # this function checks if the given transaction is valid
    # it does so by checking the following
    #   1) Is the signature of the transaction already in the cache
    #   2) Is the time of initialization of the transaction past one hour
    #   3) Is the signature of the transaction valid
    #   4) Is the sender of the transaction having enough balance
    # If even one question returns true, the transaction is treated as invalid
    def valid_transaction(self, transaction_object):
        
        if(transaction_object.signature in self.nodes.transaction_signature_cache):
            return False
        if(time.time() - transaction_object.time_of_initialization > globals.TRANSACTION_EXPIRATION):
            return False
        if(transaction_object.verify_sign() == False):
            return False
        if(self.nodes.balances.get(transaction_object.sender, 0) 
               < 
            transaction_object.amount
        ):
            return False
        return True

    # creates a new transaction, signs and returns it
    def create_new_transaction(self, receiver_key, amount):
        # initialising the transaction
        transaction = Transaction(self.key.public_key().export_key(), receiver_key, amount)
        
        # incrementing wallet nonce and setting the transaction nonce
        self.wallet_nonce+=1
        transaction.nonce = self.wallet_nonce
        
        # signing the transaction and putting the signature into the transaction.signature variable
        transaction.sign(self)
        return transaction


    # if the broadcast message is a transaction, then this function is called
    def process_transaction(self, received_transaction, wallet):
        
        # removing the first HEADER bytes of the message,
        # and then removing the padding to obtain the transaction json string
        username = ( received_transaction[13:globals.HEADER] ).strip(" ")
        transaction_json = ( received_transaction[globals.HEADER:] ).strip(" ")
        
        # turning the json string into usable object
        transaction_object = Transaction()
        transaction_object.from_json(transaction_json)

        self.nodes.usernames_to_public_keys[username] = transaction_object.sender

        # only if the transaction is valid, further processing is done
        if(self.valid_transaction(transaction_object)):
            
            # adding it to an array of transactions
            transactions_list = [transaction_object]

            # since it is now validated, we have to add it to the cache
            self.nodes.transaction_signature_cache[transaction_object.signature] = (
                transaction_object.time_of_initialization
            )

            # start creating the block in here, by fetching the blockhash of the most recent block
            block =self.miner.create_block(
                                self.nodes.block_chain[-1].block_hash,
                                transactions_list,
                                globals.LEADING_ZEROES,
                                self
                            )

            # here, 'block' has been made, now we have to check if the block
            # is valid or not, once declared valid, we check if the block_chain
            # that we have is expecting this block only, of it is not expecting
            # ie the block_hash of the last of the block_chain is not previous_block_hash
            # of the 'block' we made, then ignore this block, all this we have to do
            # to accomodate for the possibility that when we are mining for a block, but that
            # block is already mined by someone and broadcasted.
            if(block.previous_block_hash == self.nodes.block_chain[-1].block_hash):
                print("Mined, a block for a transaction")
                self.nodes.balances[wallet.key.public_key().export_key()] += 50
                self.nodes.balances[transaction_object.receiver] += transaction_object.amount
                self.nodes.balances[transaction_object.sender] -= transaction_object.amount
                self.nodes.block_chain.append(block)

                self.p2p.broadcast_block(block, self)
            else:
                pass

        else:
            ErrorMessages.ErrorMessages().invalid_transaction(transaction_object)
    
    # this is a funcion that we run in a thread to process
    # a newblock
    def process_newblock(self, received_newblock):
        
        # removing the first HEADER bytes of the messages, and then removing the padding to obtain the json of the block.
        newblock_json = ( received_newblock[globals.HEADER:] ).strip(" ")

        # extracting the username of the miner
        username = ( received_newblock[10:globals.HEADER] ).strip(" ")

        # turning the json string into usable object
        newblock_object = Block()
        newblock_object.from_json(newblock_json)

        # now, the possibilities are the following, the new block that
        # has come, 1) duplicate block, ie that block is not needed.
        # 2) nice block, ie at the end of the chain, if (2), then again
        # , we might be trying for that block, in qthat case, we have to stop our thread.
        
        # so here, we are iterating backwards from the block chain, and trying to find the fork
        iter = len(self.nodes.block_chain)-1
        while(iter >= 0 and
              self.nodes.block_chain[iter].block_hash != newblock_object.previous_block_hash
              ):
            iter-=1
        if(iter == len(self.nodes.block_chain)-1):  # if the iter stays len(array)-1, then that
                                                    # means that the block is at the end.
            # so we have to first stop the mining thread, if we are doing.
            # and later, we have to add the new received block to the block_chain.
            
            if(state_vars.currently_mining_previous_hash == newblock_object.previous_block_hash):
                # now we have to kill our mining thread, how? by empting the below state_var 
                state_vars.currently_mining_previous_hash = ""

            # appending to the block_chain
            self.nodes.block_chain.append(newblock_object)
                
            # now we also have to process the transactions in the block
            for block_transaction in newblock_object.transactions_list:
                if(block_transaction.sender != None):
                    self.nodes.balances[block_transaction.sender] -= block_transaction.amount
                else: # storing the username of the miner with his public_key
                    self.nodes.usernames_to_public_keys[username] = block_transaction.receiver
                if(block_transaction.receiver in self.nodes.balances):
                    self.nodes.balances[block_transaction.receiver] += block_transaction.amount
                else:
                    self.nodes.balances[block_transaction.receiver] = block_transaction.amount
        else:   # that means that it is a fork, in this case, generally we buffer it
                # and trust the longer chain, ie which expands more. But since this is
                # a simple model, we ignore the forks.
            pass

    # through this function, we can make a new transaction
    def make_new_transaction(self, receiver_key, amount):
        transaction_object = self.create_new_transaction(receiver_key, amount)
        self.p2p.broadcast_transaction(transaction_object, self)
        self.balance -= amount
        
