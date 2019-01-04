import os

from flask import Flask, session, render_template, redirect, request, url_for, g
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")



# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))




def main():

   # users=db.execute("SELECT id, login, password FROM users").fetchall()
  #  for user in users:   
   #     print(f"{user.id} {user.login} {user.password}")

    user_username= str(input("\n User name: "))
    user_password= str(input("\n User password: "))
    user = db.execute("SELECT id, login, password FROM users WHERE login = :login", {"login": user_username}).fetchone()
              
    

    if db.execute("SELECT id, login, password FROM users WHERE login = :login", {"login": user_username}).rowcount == 0:
        print ("user not in database")
    elif user_password == user.password:
        print(f"{user.id} {user.login} {user.password}")
        print(user_password)
        print ("password matching")
    else:
        print(f"{user.id} {user.login} {user.password}")
        print(user_password)
        print("password and login not matching")




if __name__ == "__main__":
    main()
