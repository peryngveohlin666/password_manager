from server import Database

# testing login and register for the database code
Database.register_user("test", "test", "test")

print(Database.login_user("test", "testic"))

print(Database.login_user("test", "test"))

# testing insert account and get accounts for the database code

Database.insert_account("test", "test", "test", "test")

print(Database.get_accounts("test", "test"))

Database.delete_account("test", "test", "test", "test")

print(Database.get_accounts("test", "test"))

# test change password

Database.change_user_password("test", "test", "test222222", "test")

print(Database.login_user("test", "test"))

# test update account

Database.insert_account("test", "test", "test", "test")

print(Database.get_accounts("test", "test"))

Database.change_account_password("test", "test", "test", "test", "Test2")

print(Database.get_accounts("test", "test"))