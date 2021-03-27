import concurrent.futures

import socket
import ssl
import sys
import argparse


HOST = socket.gethostbyname(socket.gethostname())
PORT = 6952
server_sni_hostname = 'example.com'
server_cert = '../server/server.crt'
client_cert = 'client.crt'
client_key = 'client.key'

BUFFER_SIZE = 4096

parser = argparse.ArgumentParser(
    description="Welcome to the DesuPassword Manager!")
parser.add_argument("--login", default=False,
                    help="login <username> <password>", nargs=2)
parser.add_argument("--logout", help="--logout",
                    action="store_const", const=True)
parser.add_argument("--register", default=False,
                    help="register <username> <password>", nargs=2)
parser.add_argument("--add-account", default=False,
                    help="--add-account <username> <password> <website> ", nargs=3)
parser.add_argument("--get-accounts", default=False,
                    help="--add-accounts <website> ", nargs=1)

args = parser.parse_args()


message = b''
response = b''


# was an argument passed
if not len(sys.argv) > 1:
    sys.exit("you did not pass any arguments, exiting.")
# one liner to open the file and extract the login and whether or not details are present
with open("login.txt", "r") as file:
    login_details = file.read()
    logged = login_details != ""


def check_logged_in():
    if not logged:
        sys.exit("you are not logged in, exiting.")


def send_message(msg):
    global message

    ongoing_message = b'' + str.encode(msg)
    message = ongoing_message


def register(username, password):
    print(' '.join(["registering:", username, password]))
    send_message(' '.join(["r:", username, password]))


def add_account(username, password, website):
    global login_details
    check_logged_in()
    print(' '.join(["adding account:", username, "for",
                    website, "with user", login_details.split(' ')[0]]))
    send_message(' '.join(["a:", login_details, username, password, website]))


def get_accounts(website):
    global login_details
    check_logged_in()

    send_message(' '.join(["g:", str(login_details), website]))


if args.login:
    with open("login.txt", "w") as auth_details:
        auth_details.write(' '.join(args.login))


if args.logout:
    with open("login.txt", "w") as auth_details:
        auth_details.write('')

if args.register:
    register(*args.register)
    with open("login.txt", "w") as auth_details:
        auth_details.write(' '.join(args.register))

if args.add_account:
    add_account(*args.add_account)

if args.get_accounts:
    get_accounts(args.get_accounts[0])


context = ssl.create_default_context(
    ssl.Purpose.SERVER_AUTH, cafile=server_cert)
context.load_cert_chain(certfile=client_cert, keyfile=client_key)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn = context.wrap_socket(
    s, server_side=False, server_hostname=server_sni_hostname)
conn.connect((HOST, PORT))


def handle_conn():
    global message
    global response
    global conn

    last_response = b''

    while True:

        # if there is a message, send it
        if message != b'':
            conn.send(message)
            message = b''

        response = conn.recv(BUFFER_SIZE)

        if response != b'' and last_response != response:
            sys.stdout.flush()
            on_message_received(str(response))
            response = b''
            last_response = response


def on_message_received(message):
    message = message[2:len(message) - 1]
    args = message.split(" ")
    if args[0] == 'ac:':
        args = args[1:]
        for arg in args:
            account = arg.split(",")
            print("Username: " + account[0], "--- Password " + account[1])
    exit()


def start_client():
    thread_executor = concurrent.futures.ThreadPoolExecutor()
    t = thread_executor.submit(handle_conn())


handle_conn()