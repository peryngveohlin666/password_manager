import concurrent.futures
import socket
import ssl
import sys
import argparse
from termcolor import colored
from pyfiglet import figlet_format
import bcrypt
from simplecrypt import encrypt, decrypt
import json

HOST = "127.0.0.1"
PORT = 6969

server_sni_hostname = 'example.com'
server_cert = '../server/server.crt'
client_cert = 'client.crt'
client_key = 'client.key'

# a client side pepper for double hashing
PEPPER = b'$2b$12$iqR2Wq8nLvhiNFmBun/4Fe'

BUFFER_SIZE = 4096

parser = argparse.ArgumentParser(prog="DesuPassword", description="Please only use one argument at a time")
parser.add_argument("--login", default=False,
                    help="login <username> <password>", nargs=2)
parser.add_argument("--logout", help="--logout",
                    action="store_const", const=True)
parser.add_argument("--register", default=False,
                    help="register <username> <password>", nargs=2)
parser.add_argument("--change-password", default=False,
                    help="--change-password <new-password>", nargs=1)
parser.add_argument("--add-account", default=False,
                    help="--add-account <username> <password> <website> ", nargs=3)
parser.add_argument("--get-accounts", default=False,
                    help="--get-accounts <website>", nargs=1)
parser.add_argument("--delete-accounts", default=False,
                    help="--delete-accounts <website>", nargs=1)
parser.add_argument("--delete-account", default=False,
                    help="--delete-account <username> <website>", nargs=2)

args = parser.parse_args()


message = b''
response = b''

encryption_password = ""

config_file = open("config.json").read()

config = json.loads(config_file)

using_authenticator = ("True" == config.get("using_authenticator"))


print(colored(figlet_format('DesuPassword'), 'green'))

# was an argument passed
if not len(sys.argv) > 1:
    sys.exit("You did not pass any arguments, exiting.")
# one liner to open the file and extract the login and whether or not details are present
with open("login.txt", "r") as file:
    login_details = file.read()

    # hash the pw
    if login_details:
        try:
            encryption_password = login_details.split(" ")[1]

            login_details = login_details.split(" ")[0] + " " + str(bcrypt.hashpw(bytes(login_details.split(" ")[1], encoding='utf8'), PEPPER))
        except:
            pass

    logged = login_details != ""


def check_logged_in():
    if not logged:
        sys.exit("You are not logged in, exiting.")


def send_message(msg):
    global message

    ongoing_message = b'' + str.encode(msg)
    message = ongoing_message


def register(username, password):
    print(colored(' '.join(["Registering:", username, password]), "red"))
    password = str(bcrypt.hashpw(bytes(password, encoding='utf8'), PEPPER))
    send_message(' '.join(["r:", username, password]))

    with open("login.txt", "w") as auth_details:
        auth_details.write(' '.join(args.register))


def add_account(username, password, website):
    global login_details
    global encryption_password
    
    encrypted_username = encrypt(encryption_password, username).hex()
    encrypted_password = encrypt(encryption_password, password).hex()
    
    hashed_website = str(bcrypt.hashpw(website.encode(), PEPPER))
    hashed_username = str(bcrypt.hashpw(username.encode(), PEPPER))

    check_logged_in()
    send_message(' '.join(["a:", login_details, encrypted_username, encrypted_password, hashed_website, hashed_username]))


def get_accounts(website):
    global login_details
    check_logged_in()

    send_message(' '.join(["g:", str(login_details), str(bcrypt.hashpw(website.encode(), PEPPER))]))


def delete_accounts(website):
    global login_details
    global encryption_password

    check_logged_in()

    send_message(' '.join(["d:", str(login_details) + " " + str(bcrypt.hashpw(website.encode(), PEPPER))]))
    
    
def delete_account(username, website):
    global login_details
    global encryption_password
    
    hashed_website = str(bcrypt.hashpw(website.encode(), PEPPER))
    hashed_username = str(bcrypt.hashpw(username.encode(), PEPPER))

    check_logged_in()

    send_message(' '.join(["d1:", str(login_details), hashed_username, hashed_website]))


def change_password(new_password):
    global login_details

    check_logged_in()

    username = login_details.split(" ")[0]

    with open("login.txt", "w") as auth_details:
        auth_details.write(username + " " + new_password)
        auth_details.close()

    new_password = str(bcrypt.hashpw(bytes(new_password, encoding='utf8'), PEPPER))

    send_message(' '.join(["cp:", login_details, new_password]))


if args.login:
    with open("login.txt", "w") as auth_details:
        auth_details.write(' '.join(args.login))
    sys.exit()


if args.logout:
    with open("login.txt", "w") as auth_details:
        auth_details.write('')
        sys.exit()

if args.register:
    register(*args.register)
    with open("login.txt", "w") as auth_details:
        auth_details.write(' '.join(args.register))

if args.add_account:
    add_account(*args.add_account)

if args.get_accounts:
    get_accounts(args.get_accounts[0])

if args.delete_accounts:
    delete_accounts(args.delete_accounts[0])

if args.change_password:
    change_password(args.change_password[0])
    
if args.delete_account:
    delete_account(*args.delete_account)

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
            if b'a:' in message or b'r:' in message or b'd:' in message or b'cp:' in message or b'd1:' in message:

                sys.exit()
            message = b''

        response = conn.recv(BUFFER_SIZE)

        if response != b'' and last_response != response:
            sys.stdout.flush()
            on_message_received(str(response))
            response = b''
            last_response = response
            sys.exit()


def on_message_received(message):
    message = message[2:len(message) - 1]
    args = message.split(" ")
    if args[0] == 'ac:':
        args = args[1:]
        try:
            i = 0
            print(colored("------------------------------------------------------------------", "cyan"))
            for arg in args:
                i+=1
                account = arg.split(",")
                print(colored("Account: ", "green") + colored(i, "yellow"))
                print(colored("Username: ", "green") + colored((decrypt(encryption_password, bytes.fromhex(account[0]))).decode('utf8'), "blue"))
                tmp_pass = (decrypt(encryption_password, bytes.fromhex(account[1]))).decode('utf8')
                print(colored("Password: " , "green") + colored(tmp_pass, "red"))
                print(colored(len("Password: " + tmp_pass) * "-", "cyan"))
        except:
            print(colored("You have no accounts for this service", "cyan"))

    exit()


def start_client():
    thread_executor = concurrent.futures.ThreadPoolExecutor()
    t = thread_executor.submit(handle_conn())


handle_conn()