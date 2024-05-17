import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("7.tcp.eu.ngrok.io", 14248))

print(client.recv(1024).decode('ascii'))
client.send("Hey Server".encode('ascii'))
 