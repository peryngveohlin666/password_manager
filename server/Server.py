import Database
import socket
import ssl
import concurrent.futures
import sys
import bcrypt


HOST = socket.gethostbyname(socket.gethostname())
PORT = 6966

server_cert = 'server.crt'
server_key = 'server.key'
client_certs = '../client/client.crt'

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.verify_mode = ssl.CERT_REQUIRED
context.load_cert_chain(certfile=server_cert, keyfile=server_key)
context.load_verify_locations(cafile=client_certs)

bindsocket = socket.socket()
bindsocket.bind((HOST, PORT))
bindsocket.listen(5)

BUFFER_SIZE = 4096

threads = []


def register(username, password):
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password, salt)
    Database.register_user(username, password_hash, salt)


def login(username, password):
    salt = Database.get_salt(username)
    password_hash = bcrypt.hashpw(password, salt)
    return Database.login_user(username, password_hash)

def on_message_received(message):
    info = message.split(" ")
    command = info[0]
    if command == "b'l:":
        login(info[1], info[2])
        message = "your tried to log in to " + info[1]
    if command == "b'r:":
        print("test")
        register(info[1], info[2])
        print(login(info[1],info[2]))
        print("after")
        message = "your tried to register " + info[1] + " " + info[2]
    print(message)
    return(message)


def handle_client(sock):
    try:
        print("Client connected: {}:{}".format(fromaddr[0], fromaddr[1]))
        conn = context.wrap_socket(sock, server_side=True)
        print("SSL established. Peer: {}".format(conn.getpeercert()))
        while True:
            data = conn.recv(BUFFER_SIZE)
            sock.send(on_message_received(str(data)))
    finally:
        pass
    #     print("Closing connection")
    #     sys.stdout.flush()
    #     conn.shutdown(socket.SHUT_RDWR)
    #     conn.close()


while True:
    print("Waiting for client")
    newsocket, fromaddr = bindsocket.accept()
    thread_executor = concurrent.futures.ThreadPoolExecutor()
    t = thread_executor.submit(handle_client, newsocket)
    threads.append(t)
