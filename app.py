from warnings import warn
from P2P import P2P
from Wallet import Wallet
from Nodes import Nodes
from Crypto.PublicKey import RSA
from Miner import Miner
import threading
import globals

# take username from the user
username = input("Enter username:")
wallet = Wallet(username)

listening_thread = threading.Thread(target=wallet.p2p.listen, args=(wallet,), daemon=True)
listening_thread.start()


# this wrap up function is used to pay someone
def pay(username, amount):
    wallet.make_new_transaction(wallet.nodes.usernames_to_public_keys[username], amount)
    print("Paid " + username + ":" + str(amount))

# this wrap up function is used to list the balances
def balances():
    for user, pk in wallet.nodes.usernames_to_public_keys.items():
        print(user + ":" + str(wallet.nodes.balances[wallet.nodes.usernames_to_public_keys[user]]))

# through this wrap up, a user can mine in order to get the BLOCK_REWARD
def mine_for_reward():
    wallet.miner.create_reward_block(wallet)
    print("Mined a block, got " + str(globals.BLOCK_REWARD) + ".")
