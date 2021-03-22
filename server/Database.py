import datetime, pymongo
from pymongo import MongoClient

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



# register a user in the database, take a username a password hash and the password salt as the input
def register_user(username, password_hash, password_salt):
    global users_collection
    if not users_collection.find_one({"username": username}):
        users_collection.insert_one(
            {"username": username, "password_hash": password_hash, "password_salt": password_salt})


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
def change_user_password(username, password_hash, new_password_hash, new_password_salt):
    global users_collection
    try:
        user = {"username": username, "password_hash": password_hash}
        new_password = {"$set": {"password_hash": new_password_hash, "password_salt": new_password_salt}}

        users_collection.update_one(user, new_password)
    except Exception:
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
