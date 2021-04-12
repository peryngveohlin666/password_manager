import datetime, pymongo
from pymongo import MongoClient
import socket
import ssl
import concurrent.futures
import sys
import bcrypt

# read the login details for the database
uri = open("mongo.txt").read()

# initialize the cluster
cluster = MongoClient(uri)

# initialize the database
database = cluster["Database"]

# initialize the users collection
users_collection = database["Users"]

# initialize the accounts collection
accounts_collection = database["Accounts"]


HOST = "172.31.7.18"
PORT = 6967

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


# register a user in the database, take a username a password hash and the password salt as the input
def register_user(username, password_hash, password_salt):
    global users_collection
    if not users_collection.find_one({"username": username}):
        users_collection.insert_one(
            {"username": username, "password_hash": password_hash, "password_salt": password_salt})


def get_salt(username):
    global users_collection
    try:
        user = users_collection.find_one({"username": username})
        return user["password_salt"]
    except Exception:
        return ""


# compare the password hash to the one stored in the database for the username and return true if they are the same
# return false otherwise, return false on error
def login_user(username, password_hash):
    global users_collection
    try:
        user = users_collection.find_one({"username": username})
        return user["password_hash"] == password_hash
    except Exception:
        return False


# change the password for a user
def change_user_password(username, password, new_password):
    global users_collection

    print("salting")

    salt = get_salt(username)
    password_hash = bcrypt.hashpw(bytes(password, 'utf-8'), salt)
    print("salted")

    new_password_salt = bcrypt.gensalt()
    print("salted2")

    new_password_hash = bcrypt.hashpw(bytes(new_password, 'utf-8'), new_password_salt)
    print("hashed")

    try:
        user = {"username": username, "password_hash": password_hash}
        new_password = {"$set": {"password_hash": new_password_hash, "password_salt": new_password_salt}}

        users_collection.update_one(user, new_password)
    except Exception:
        print("exception")
        pass


# get the accounts for a website for the owner (which is the username for the logged in user. Return a list of comma
# separated username and passwords like: ["username,password,description", "username2,password2,description2"].
def get_accounts(owner, website):
    global accounts_collection
    try:
        accounts_list = []
        accounts = accounts_collection.find({"owner": owner, "website": website})
        for account in accounts:
            tmp_account = account["username"] + "," + account["password"] + "," + account["description"]
            accounts_list.append(tmp_account)
        return accounts_list
    except Exception:
        return []


# insert a new account to the database
def insert_account(owner, username, password, website, description=""):
    global accounts_collection
    accounts_collection.insert_one(
        {"owner": owner, "username": username, "password": password, "website": website, "description": description})


# delete an account from the database
def delete_account(owner, username, password, website, description=""):
    global accounts_collection
    accounts_collection.delete_one(
        {"owner": owner, "username": username, "password": password, "website": website, "description": description})


# update an accounts password
def change_account_password(owner, username, password, website, new_password):
    global accounts_collection
    account = {"owner": owner, "username": username, "password": password, "website": website}
    new_password = {"$set": {"password": new_password}}

    accounts_collection.update_one(account, new_password)


def register(username, password):
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(bytes(password, 'utf-8'), salt)
    register_user(username, password_hash, salt)


def login(username, password):
    salt = get_salt(username)
    password_hash = bcrypt.hashpw(bytes(password, 'utf-8'), salt)
    return login_user(username, password_hash)


def handle_client(sock):
    print("Client connected: {}:{}".format(fromaddr[0], fromaddr[1]))
    conn = context.wrap_socket(sock, server_side=True)
    print("SSL established. Peer: {}".format(conn.getpeercert()))
    last_data = b''
    while True:
        data = conn.recv(BUFFER_SIZE)
        if data != last_data:
            print(data)
            message = str(data)
            message = message[2:len(message) - 1]
            args = message.split(" ")
            print(args)
            if args[0] == 'r:':
                register(args[1], args[2])
            if args[0] == 'a:':
                print("a")
                if login(args[1], args[2]):
                    print("logged in")
                    insert_account(args[1], args[3], args[4], args[5])
            if args[0] == 'g:':
                print("g")
              #  print(args[1],args[2])
                if login(args[1], args[2]):
                    print("logged")
                    accounts = get_accounts(args[1], args[3])
                    accounts_str = ""
                    print(accounts)
                    for account in accounts:
                        accounts_str += account
                        accounts_str += " "
                    accounts_str = accounts_str[0:len(accounts_str) - 1]
                    print(accounts_str)
                    conn.send(bytes("ac: " + accounts_str, "utf-8"))
                    print("sent")
            if args[0] == 'd:':
                if login(args[1], args[2]):
                    delete_account(args[1], args[3], args[4], args[5])
            if args[0] == 'cp:':
                print(args)
                if login(args[1], args[2]):
                    change_user_password(args[1], args[2], args[3])




        last_data = data


while True:
    print("Waiting for client")
    newsocket, fromaddr = bindsocket.accept()
    thread_executor = concurrent.futures.ThreadPoolExecutor()
    t = thread_executor.submit(handle_client, newsocket)
    threads.append(t)
