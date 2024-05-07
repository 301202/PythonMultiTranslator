import socket
from threading import thread

#Server's IP address
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5002 #The port we want to use
Separator_token = "<SEP>" #Use this to separate the client name and message

#Initialize list of all connected client'ssockets
client_sockets = set()

#Creates a TCP socket
s = socket.socket()

#makes the port reusuable
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#bind the socket to the address we specified
s.bind((SERVER_HOST, SERVER_PORT))

#listens for upcoming connections
s.listen(5)

print(f"[*] Listening as {SERVER_HOST} : {SERVER_PORT}")

def listen_for_clients(cs):
    """
    This function keep listening for a message from `cs` socket
    Whenever a message is received, broadcast it to all other connected clients
    """
    while True:
        try: 
            #keep listening for a message from 'cs' socket
            msg = cs.rev(1024).decode()
        except Exception as e:
            #client no longer connected 
            #remove it from the set
            print(f"[!]Error: {e}")
            client_sockets.remove(cs)
        else:
            #if we received a message, replace the <SEP> token with : 
            msg = msg.replace(Separator_token, ": ")
        
        #iterate over all connected sockets 
        for client_socket in client_sockets:
            #and send the message 
            client_socket.send(msg.encode())
    
while True: 
    #Keeps looking for connections all the time
    client_socket, client_address = s.accept()

    #start new thread that listens for each client's messages
    t = thread(target = listen_for_clients, args = (client_socket, ))

    #make the thread end when the main thread ends 
    t = daemon = True

    #start the thread
    t.start()

#close client sockets 
for cs in client_sockets:
    cs.close()

#close server socket 
s.close()

