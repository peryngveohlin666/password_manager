# https://docs.python.org/3/library/argparse.html

import argparse
import os.path
import Client
#need to finish server side first.



parser = argparse.ArgumentParser(description="Welcome to the DesuPassword Manager!")

parser.add_argument("--login", default=False, help="login help")

txtFile = open("login.txt", "a+")

website_name_message = 'Please enter the website you want credentials for'
#get the size of the txt file, used to check of the existence of an PM account
txtSize = os.path.getsize('login.txt')
#print(txtSize)

# if txtSize > 0:
#     #login to the password manager
#     # def login(username, password):
#     #     pass
#     print(website_name_message)
#     #function that retrieves the website username and password with description
#     def get_account():
#     #mongo get requests then post onto command line


if txtSize == 0:
    # run the register function to make a
    def register_account():
        txtFile.writelines(input("Enter your username for the password manager: " + "\n"))

        txtFile.writelines(input("Enter the password for the password manager: " + "\n"))
    register_account()



args = parser.parse_args()


Client.register("hi","there")
Client.start_client()