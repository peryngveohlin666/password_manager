import socket
import time

HOST = '127.0.0.1'
PORT = 7016


def request(username, password):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
        soc.connect((HOST, PORT))
        soc.sendall(str.encode("let me in"))
        while True:

            message = soc.recv(1024)
            if str(message).startswith('b\'please login'):
                print("why?")
                soc.sendall(str.encode('login ' +username+' '+password))
                time.sleep(1)
            print(message)
