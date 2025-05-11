# this is a class for all the invalid messages and error messages, maybe warnings and all
class ErrorMessages:

    # this function is called if a broadcast message that we received is invalid
    def invalid_broadcast(self, received_data_decode):
        print("Received an invalid broadcast message. Ignoring.")

    # this function is called if a transaction that we received is invalid
    def invalid_transaction(self, transaction_object):
        print("The received transaction is invalid.")
    
    # this function is called if a transaction that we recieved was already processed
    def repeat_transaction(self, transaction_object):
        print("The transaction has already been processed")
