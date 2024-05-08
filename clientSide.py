import socket
import threading
import googletrans
from googletrans import Translator

translator = Translator()

nickname = input("Choose a nickname: ")

print("Here are the list of languages:")
print(googletrans.LANGUAGES)

lang = input("Please enter your language of choice: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))

def receive():
    while True:
        try:
            message =  client.recv(1024).decode()
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
            else:
                detectedLang = translator.detect(message).lang.lower()
                translation = translator.translate(message[message.index("]")+1:], src=detectedLang, dest=lang)
                print(message)
        except:
            print("An error occurred!")
            client.closed()
            break

def write():
    while True:
        message = f'{nickname}: {input("")}'
        if message == "!q":
            client.close()
            break
        else:
            client.send(f"[{lang}]{message}".encode('ascii'))

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
