import concurrent.futures

import socket
import ssl

HOST = socket.gethostbyname(socket.gethostname())
PORT = 7777
server_sni_hostname = 'example.com'
server_cert = '../server/server.crt'
client_cert = 'client.crt'
client_key = 'client.key'

BUFFER_SIZE = 4096

context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=server_cert)
context.load_cert_chain(certfile=client_cert, keyfile=client_key)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn = context.wrap_socket(s, server_side=False, server_hostname=server_sni_hostname)
conn.connect((HOST, PORT))
print("SSL established. Peer: {}".format(conn.getpeercert()))

message = b''
response = b''


def handle_conn():
    global message
    global response
    global conn

    while True:

        # if there is a message, send it
        if message != b'':
            conn.send(message)
            message = b''
            print("message = ")
            print(message)

        response = conn.recv(BUFFER_SIZE)
        if response != b'':
            on_message_received(response)
            response = b''


def on_message_received(message):
    print("response ")
    print(message)
    send_message(message)


def send_message(msg):
    global message

    ongoing_message = b'' + str.encode(msg)
    message = ongoing_message


def login(username, password):
    send_message("l:" + username + "𝄫" + password)

print("logging in")
login("super", "sexy")

thread_executor = concurrent.futures.ThreadPoolExecutor()
t = thread_executor.submit(handle_conn())
