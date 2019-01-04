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

    users=db.execute("SELECT id, login, password FROM users").fetchall()
    for user in users:   
        print(f"{user.id} {user.login} {user.password}")
    print("I am here")

if __name__ == "__main__":
    main()
