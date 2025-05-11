import socket
import threading
import globals
import ErrorMessages
import json

# this is the class where all the broadcasting and listening is handled
class P2P:
    # a function which broadcasts a message to 5050 port
    def broadcast(self, message):
        # create a UDP socket to broadcast the message
        sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        #setting the option of the socket in order to broadcast messages
        sender_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # broadcasting the message
        sender_socket.sendto(message.encode(), (globals.BROADCAST_IP, globals.BROADCAST_PORT))


    # this function listens to broadcast messages in the PORT 
    def listen(self, wallet):
        
        # defining a listen socket where all broadcast messages are handled
        # socket.SOCK_DGRAM means UDP packets
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # enabling listening to broadcast messages in the socket config
        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # binding the socket to the respective LOCAL_LISTENING_PORT
        listen_socket.bind((globals.BROADCAST_IP, globals.BROADCAST_PORT))
        i=5
        while(i>0):
            i-=1
            # listening for UDP packets, and storing the received message in received_data varible
            received_data, sender_address = listen_socket.recvfrom(globals.MESSAGE_SIZE)
            
            # checking if it is a new node, if it is then appending it to the list of nodes
            if sender_address[0] in wallet.nodes.ip_addresses:
                pass
            else:
                wallet.nodes.ip_addresses.append(sender_address[0])

            # processing the received data
            received_data_decode = received_data.decode()
            
            # now, the received data can be either a block or a transaction.

            # if it is transaction, then start a thread to process it
            if(received_data_decode[:13] == "[TRANSACTION]"):
                process_transaction_thread = threading.Thread(target=wallet.process_transaction, args=(received_data_decode,wallet), daemon=True)
                process_transaction_thread.start()

            # if the broadcast message received is a new block,
            # we start a thread to start processing it
            elif(received_data_decode[:10] == "[NEWBLOCK]"):
                process_newblock_thread = threading.Thread(target=wallet.process_newblock, args=(received_data_decode,), daemon=True)
                process_newblock_thread.start()

            else:
                ErrorMessages.ErrorMessages().invalid_broadcast(received_data_decode)
                
    # this function is used to broadcast blocks that we mine
    def broadcast_block(self, block, wallet):
        block_json = block.to_json()
        broadcast_messsage ="[NEWBLOCK]" + str(wallet.username) + " "*(globals.HEADER-(10+len(wallet.username))) + block_json
        broadcast_messsage = broadcast_messsage + " "*( (globals.MESSAGE_SIZE)-len(broadcast_messsage) )
        self.broadcast(broadcast_messsage)

    # this function is used to broadcast transactions that we do
    def broadcast_transaction(self, transaction_object, wallet):
        transaction_json = transaction_object.to_json() 
        broadcast_message = "[TRANSACTION]" + str(wallet.username) + " "*(globals.HEADER-(13+len(wallet.username))) + transaction_json
        broadcast_message = broadcast_message + " "*( (globals.MESSAGE_SIZE)-len(broadcast_message) )
        self.broadcast(broadcast_message)

                    
