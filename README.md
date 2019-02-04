# Project 1
Web Programming with Python and JavaScript

This is Project 1 for CS50W.
The goal is to create a website using Python, PostgreSQL, HTML and CSS in a Flask framework to create a book review website. The website needs to use the Goodreads API and provide users with it's own API to return book data when an ISBN is submitted.

The database for the website is hosted at:
postgres://eifdrzqcgxzhck:6271812f9867d112cb45fca315a0ef24ae22c80822717339f8ac4dd07cc43bf7@ec2-54-247-74-131.eu-west-1.compute.amazonaws.com:5432/d8pbjfq3vgb8f1

import.py is used to import a CSV file (books.csv) in the PSQL database. It contains the data related to 5000 books from the Goodreads database

styles.css in static is used to modify some of the bootstrap formatting used in the website

The templates folder contains all the html pages to be rendered by the python code.

application.py is python code for the website, it processes user inputs and manages interactions with the database to render the required html pages. It also contains the API at the bottom



