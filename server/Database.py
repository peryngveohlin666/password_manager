import datetime

def register_user(username, password_hash):
    pass


def login(username, password_hash):
    return True


def get_accounts(website):
    return ["username,password", "username2,password2"]


def insert_account(username, password, website, description=""):
    added_date = datetime.datetime.now()
