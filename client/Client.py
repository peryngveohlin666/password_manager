import concurrent.futures

import socket
import ssl
import sys
import argparse
import os.path


HOST = socket.gethostbyname(socket.gethostname())
PORT = 6954
server_sni_hostname = 'example.com'
server_cert = '../server/server.crt'
client_cert = 'client.crt'
client_key = 'client.key'

BUFFER_SIZE = 4096

parser = argparse.ArgumentParser(description="Welcome to the DesuPassword Manager!")
parser.add_argument("--login", default=False, help="login <username> <password>", nargs=2)
parser.add_argument("--register", default=False, help="register <username> <password>", nargs=2)
parser.add_argument("--add-account", default=False, help="--add_account <username> <password> <website> ", nargs=3)

args = parser.parse_args()
print(args)


message = b''
response = b''


txt_file = open("login.txt", "r")
login_details = txt_file.read()
txt_file.close()


def send_message(msg):
    global message

    ongoing_message = b'' + str.encode(msg)
    message = ongoing_message


def register(username, password):
    send_message("r: " + username + " " + password)


def add_account(username, password, website):
    global login_details
    send_message("a: " + login_details + " " + username + " " + password + " " + website)


if args.login:
    auth_details = open("login.txt", "w")

    auth_details.write(args.login[0] + " " + args.login[1])
    auth_details.close()

if args.register:
    r_username = args.register[0]

    r_password = args.register[1]

    register(r_username, r_password)

    auth_details = open("login.txt", "w")

    auth_details.write(args.register[0] + " " + args.register[1])

    auth_details.close()

if args.add_account:

    account_name = args.add_account[0]

    account_password = args.add_account[1]

    account_website = args.add_account[2]

    add_account(account_name, account_password, account_website)


context = ssl.create_default_context(
    ssl.Purpose.SERVER_AUTH, cafile=server_cert)
context.load_cert_chain(certfile=client_cert, keyfile=client_key)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn = context.wrap_socket(
    s, server_side=False, server_hostname=server_sni_hostname)
conn.connect((HOST, PORT))
print("SSL established. Peer: {}".format(conn.getpeercert()))


def handle_conn():
    global message
    global response
    global conn

    while True:

        # if there is a message, send it
        if message != b'':
            conn.send(message)
            message = b''

        response = conn.recv(BUFFER_SIZE)

        if response != b'':
            print(response)
            sys.stdout.flush()
            on_message_received(str(response))
            response = b''


def on_message_received(message):
    print("response: " + str(message))
    sys.stdout.flush()


def start_client():
    thread_executor = concurrent.futures.ThreadPoolExecutor()
    t = thread_executor.submit(handle_conn())


handle_conn()