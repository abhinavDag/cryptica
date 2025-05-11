from base64 import b64encode
from json import decoder
import time
from Crypto.PublicKey import RSA
import json
from base64 import b64encode, b64decode
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

# we can create an object of each transaction using this class
class Transaction:
    def __init__(self, sender=None, receiver=None, amount=None):
        
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.time_of_initialization = time.time()
        self.nonce = 0
        self.signature = None

    # a function to convert itself to a json
    def to_json(self):
        
        sender = None if self.sender is None else self.sender.decode('utf-8')
        receiver = None if self.receiver is None else self.receiver.decode('utf-8')
        transaction_dict = {
            "sender": sender,
            "receiver": receiver,
            "amount": self.amount,
            "time_of_initialization": self.time_of_initialization,
            "nonce": self.nonce,
        }
        if(self.signature is not None):
            transaction_dict['signature'] = b64encode(self.signature).decode('utf-8')
        else:
            transaction_dict['signature'] = None
    
        transaction_json = json.dumps(transaction_dict)
        return transaction_json

    # a function which takes in json, and makes a transaction object
    def from_json(self, transaction_json):
        
        transaction_dict = json.loads(transaction_json)
        if(transaction_dict['sender'] != None):
            sender = transaction_dict['sender'].encode('utf-8')
        else:
            sender = None
        receiver = transaction_dict['receiver'].encode('utf-8')
        
        self.sender  = sender
        self.receiver = receiver
        self.amount = transaction_dict['amount']
        self.time_of_initialization = transaction_dict['time_of_initialization']
        self.nonce = transaction_dict['nonce']
        if "signature" in transaction_json and transaction_dict["signature"]:
            self.signature = b64decode(transaction_dict["signature"])
        else:
            self.signature = None

    # adds signature to the transaction using the private key
    def sign(self, wallet):

        transaction_json_string = self.to_json()
        transaction_hash = SHA256.new(transaction_json_string.encode())
        signature = pkcs1_15.new(wallet.key).sign(transaction_hash)
        self.signature = signature

    # takes in transaction and then returns True if signature is valid and False otherwise
    def verify_sign(self):

        if self.signature is None:
            return False
        # copying the signature for verification process
        signature = self.signature

        # in the transaction setting signature to None
        self.signature = None

        # making another json string in order to calculate the hash
        calculated_json_string = self.to_json()

        calculated_hash = SHA256.new(calculated_json_string.encode())

        try:
            sender_key = RSA.import_key(self.sender)
            pkcs1_15.new(sender_key).verify(calculated_hash, signature)
            return True
        except:
            return False



