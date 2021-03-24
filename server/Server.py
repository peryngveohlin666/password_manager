import socket
import ssl
import concurrent.futures
import sys

HOST = socket.gethostbyname(socket.gethostname())
PORT = 7777

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


def handle_client(sock):
    username = ""

    try:
        print("Client connected: {}:{}".format(fromaddr[0], fromaddr[1]))
        conn = context.wrap_socket(sock, server_side=True)
        print("SSL established. Peer: {}".format(conn.getpeercert()))

        buf = b''  # Buffer to hold received client data
        while True:
            data = conn.recv(BUFFER_SIZE)
            string_data = str(data)
            print(string_data)
            # if string_data.startswith("l:"):

    finally:
        print("Closing connection")
        sys.stdout.flush()
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()


while True:
    print("Waiting for client")
    newsocket, fromaddr = bindsocket.accept()
    thread_executor = concurrent.futures.ThreadPoolExecutor()
    t = thread_executor.submit(handle_client, newsocket)
    threads.append(t)
