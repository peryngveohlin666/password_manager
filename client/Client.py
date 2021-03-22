import socket
import ssl
import time

import socket
import ssl

HOST = socket.gethostbyname(socket.gethostname())
PORT = 7777
server_sni_hostname = 'example.com'
server_cert = '../server/server.crt'
client_cert = 'client.crt'
client_key = 'client.key'

context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=server_cert)
context.load_cert_chain(certfile=client_cert, keyfile=client_key)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn = context.wrap_socket(s, server_side=False, server_hostname=server_sni_hostname)
conn.connect((HOST, PORT))
print("SSL established. Peer: {}".format(conn.getpeercert()))
print("Sending: 'Hello, world!")
conn.send(b"Hello, world!")
print("Closing connection")
conn.close()






# def request(username, password):
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
#         soc.connect((HOST, PORT))
#         soc.sendall(str.encode("let me in"))
#         while True:
#
#             message = soc.recv(1024)
#             if str(message).startswith('b\'please login'):
#                 print("why?")
#                 soc.sendall(str.encode('login ' +username+' '+password))
#                 time.sleep(1)
#             print(message)
