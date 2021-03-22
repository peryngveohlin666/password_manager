import socket
import ssl
import time
import Database


# HOST = '127.0.0.1'
# PORT = 7016
# LOGGED = False
#
# bufSize = 1024

# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
#     soc.bind((HOST, PORT))
#     soc.listen()
#     connection, address = soc.accept()
#     with connection:
#         while True:
#             message = connection.recv(bufSize)
#             while not LOGGED:
#                 print(message)
#                 if (str(message)).startswith('b\'login'):
#                     LOGGED = True
#                     print("nice")
#                     break
#                 connection.sendall(str.encode("please login"))
#                 time.sleep(1)
#                 break
#             print(message)


import socket
import ssl

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

while True:
    print("Waiting for client")
    newsocket, fromaddr = bindsocket.accept()
    print("Client connected: {}:{}".format(fromaddr[0], fromaddr[1]))
    conn = context.wrap_socket(newsocket, server_side=True)
    print("SSL established. Peer: {}".format(conn.getpeercert()))
    buf = b''  # Buffer to hold received client data
    try:
        while True:
            data = conn.recv(4096)
            if data:
                # Client sent us data. Append to buffer
                buf += data
            else:
                # No more data from client. Show buffer and close connection.
                print("Received:", buf)
                break
    finally:
        print("Closing connection")
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()
