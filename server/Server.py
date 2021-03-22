import socket
import time
import Database


HOST = '127.0.0.1'
PORT = 7016
LOGGED= False

bufSize = 1024

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
    soc.bind((HOST, PORT))
    soc.listen()
    connection, address = soc.accept()
    with connection:
        while True:
            message = connection.recv(bufSize)
            while not LOGGED:
                print(message)
                if (str(message)).startswith('b\'login'):
                    LOGGED = True
                    print("nice")
                    break
                connection.sendall(str.encode("please login"))
                time.sleep(1)
                break
            print(message)
