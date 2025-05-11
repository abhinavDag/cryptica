import json
from socket import create_connection
import Block
import script
import state_vars
import globals
from Transaction import Transaction

# this class deals with creating a block, once the received transactions are perfectly valid
class Miner:

    # this function creates the transaction which gives
    # the miner BLOCK_REWARD number of coins
    def create_block_reward_transaction(self, wallet):
        block_reward_transaction = Transaction(
                                        sender=None,
                                        receiver=wallet.key.public_key().export_key(), 
                                        amount=globals.BLOCK_REWARD
                                    )
        return block_reward_transaction

    # generates the nonce which is the special number in mining, this
    # function is the one that runs for lot of time
    def nonce_generator(self, block_json, leading_zeroes):
        
        nonce = 0
        modified_block_json = block_json + str(nonce)
        while(
            not script.valid_block_hash(script.sha256_bits_str(modified_block_json), leading_zeroes) 
            and state_vars.currently_mining_previous_hash != ""
        ):
            nonce+=1
            modified_block_json = block_json + str(nonce)
        return nonce 
        
    #this function creates a block to add to the block chain
    def create_block(self, previous_block_hash, transactions_list, leading_zeroes, wallet):
        
        block_reward_transaction = self.create_block_reward_transaction(wallet)
        transactions_list.append(block_reward_transaction)
        state_vars.currently_mining_previous_hash = previous_block_hash
        block = Block.Block(previous_block_hash, transactions_list)
        block_json = block.to_json()
        nonce = self.nonce_generator(block_json, leading_zeroes)
        block.block_hash = script.sha256_bits_str(block_json+str(nonce))
        block.nonce = nonce
        return block

    # this function gives us a block containing only one transaction which is
    # miner gets BLOCK_REWARD
    def create_reward_block(self, wallet):
        
        block = self.create_block(
                        wallet.nodes.block_chain[-1].block_hash, 
                        [], 
                        globals.LEADING_ZEROES,
                        wallet
                    )
        
        # now, the block that we mined maybe useless because by the
        # time we mined it, maybe some other block got broadcasted,
        # and appended into the block_chain
        if(block.previous_block_hash == wallet.nodes.block_chain[-1].block_hash):
            wallet.nodes.balances[wallet.key.public_key().export_key()]+=globals.BLOCK_REWARD
            wallet.nodes.block_chain.append(block)
            wallet.p2p.broadcast_block(block, wallet)
        else:
            self.create_reward_block(wallet)


