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
client.connect(("0.tcp.eu.ngrok.io", 11554))


def receive():
    while True:
        try:
            message =  client.recv(1024).decode('ascii')
            detectedLang = translator.detect(message).lang.lower()
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
            else:
                translation = translator.translate(message, src=detectedLang, dest=lang)
                print(translation.text)
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
            client.send(f"{message}".encode())

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
