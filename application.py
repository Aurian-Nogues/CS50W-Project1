import os
import requests
from flask import Flask, session, render_template, redirect, request, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


#index page, handles the login 
@app.route('/', methods= ['GET', 'POST'])
def index():
    if request.method =='POST' :
        session.pop('user', None) 

        submitted_username = request.form['username']
        submitted_password = request.form['password']
        user = db.execute("SELECT id, login, password FROM users WHERE login = :login", {"login": submitted_username}).fetchone()
    
        if db.execute("SELECT id, login, password FROM users WHERE login = :login", {"login": submitted_username}).rowcount == 0:
            error=("Username doesn't exist, please check spelling or create an account")
            return render_template("failed.html", error=error)
        elif submitted_password != user.password:
            error=("Wrong password")
            return render_template("failed.html", error=error)
        elif submitted_password == user.password:
             session['user'] = user.login
             return redirect(url_for('search'))

    
    else:
        return render_template("index.html")

#register page, handles addition of new users
@app.route('/register', methods= ['POST', 'GET'])
def register():
    if request.method == "GET" :
        return render_template("register.html")

    elif request.method == 'POST' :
        session.pop('user', None)
        submitted_username = request.form['username']
        submitted_password = request.form['password']

        #only add user in database if there is no userexisting user with the same login
        if db.execute("SELECT id, login, password FROM users WHERE login = :login", {"login": submitted_username}).rowcount == 0:
            db.execute("INSERT INTO users (login, password) Values (:login, :password)", {"login": submitted_username, "password": submitted_password})
            db.commit()
            success=("Successfully created a new account, your username is: ")
            return render_template("creation_succes.html", success=success, username=submitted_username)
        else:
            error=("The username you selected already exists, please select another username")
            return render_template("failed.html", error=error)


#page reached once logged in
@app.route('/search', methods= ['POST', 'GET'])
def search():

    if request.method == 'POST' :
        books = None
        searchtype = request.form['searchtype']
        keyword = request.form['keyword']

        if keyword == "":
            books = db.execute("SELECT * FROM books").fetchall()
        
        elif searchtype == "year":
            books = db.execute("SELECT * FROM books WHERE year = :keyword",
                                {"keyword": keyword}).fetchall()

        elif searchtype == "title":
            keyword = f'%{keyword}%'
            books = db.execute("SELECT * FROM books WHERE title ILIKE :keyword",
                                {"keyword": keyword}).fetchall()
        elif searchtype == "author":
            keyword = f'%{keyword}%'
            books = db.execute("SELECT * FROM books WHERE author ILIKE :keyword",
                                {"keyword": keyword}).fetchall() 
        elif searchtype == "isbn":
            keyword = f'%{keyword}%'
            books = db.execute("SELECT * FROM books WHERE isbn ILIKE :keyword",
                                {"keyword": keyword}).fetchall() 
        
        return render_template('search.html', books=books)
    else :
        books = db.execute("SELECT * FROM books").fetchall()
    return render_template('search.html', books=books)          

#book page
@app.route('/book/<int:id>', methods = ['POST', 'GET'])
def book(id):

    if request.method == "POST" : 
        #route if you submit a review then confirm it
        if request.form['status'] == 'Confirm':

            
            review = session['review']
            rating = session['rating']
            username = session['user']
            avgRating = session['avgRating']
            nbrRatings = session['nbrRatings']
            isbn = session['book'].isbn
            db.execute("INSERT INTO reviews (isbn, username, review, rating) Values (:isbn, :username, :review, :rating)", {"isbn": isbn, "username": username, "review": review, "rating": rating})
            db.commit()

            reviews = db.execute("SELECT * FROM reviews WHERE isbn = :isbn ORDER BY id DESC" ,
                                {"isbn": isbn}).fetchall()

            reviewed = 'reviewed'

            return render_template('book.html', reviews=reviews, reviewed = reviewed, avgRating = avgRating,nbrRatings = nbrRatings )
        
        #route if you submit a review or edit it
        else:   
            session['review'] = request.form['review']
            session['rating'] = request.form['rating']
            return render_template('review.html')

    #route if you arrive on the book page from a search
    
    session['id'] = id
    session['book'] = db.execute("SELECT * FROM books WHERE id = :id", {"id": id}).fetchone()
    isbn = session['book'].isbn
    reviews = db.execute("SELECT * FROM reviews WHERE isbn = :isbn ORDER BY id DESC",
                                {"isbn": isbn}).fetchall()

    #use goodreads API to get book rating and number of ratings

    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "sAEPXUb5EvhHgSe5ECViNQ", "isbns": isbn})
    data = res.json()
    session['avgRating'] = data['books'][0]['average_rating']
    session['nbrRatings'] = data['books'][0]['work_ratings_count']

    avgRating = session['avgRating']
    nbrRatings = session['nbrRatings']
    
    #test if user already reviewed the book
    title = session['book'].title
    username = session['user']
    reviewed = db.execute("SELECT * from reviews INNER JOIN books ON reviews.isbn = books.isbn WHERE title = :title and username = :username", {"title": title, "username": username}).fetchone()
    if reviewed is None:
       reviewed = 'not reviewed'
    else:
        reviewed = 'reviewed'
      
    return render_template('book.html', reviews=reviews, reviewed = reviewed, avgRating = avgRating,nbrRatings = nbrRatings)

#display all reviews
@app.route('/allReviews')
def allReviews():
    reviews = db.execute("SELECT * from reviews INNER JOIN books ON reviews.isbn = books.isbn").fetchall()

    return render_template('allReviews.html', reviews=reviews)

#display my reviews reviews
@app.route('/myReviews')
def myReviews():
    username = session['user']
    title = session['book'].title
    reviews = db.execute("SELECT * from reviews INNER JOIN books ON reviews.isbn = books.isbn WHERE username = :username", {"username": username}).fetchall()

    return render_template('myReviews.html', reviews=reviews)


#log out page
@app.route('/logout')
def logout():
    session.pop('user', None)
    return render_template('logout.html')

@app.route('/getsession')
def getsession():
    if 'user' in session:
        return session ['user']
    
    return 'not logged in!'
 

@app.route("/api/<isbn>")

def book_api(isbn):

    book = db.execute("SELECT * FROM books WHERE isbn = :isbn",
                                {"isbn": isbn}).fetchone()
    if book is None:
        return jsonify({
            "error": "isbn not found"
        }), 404

    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "sAEPXUb5EvhHgSe5ECViNQ", "isbns": isbn})
    data = res.json()


    title = book.title
    author = book.author
    year = book.year
    reviews = data['books'][0]['work_ratings_count']
    score = data['books'][0]['average_rating']

    return jsonify({
        "title": title,
        "author": author,
        "year": year,
        "isbn": isbn,
        "review_count": reviews,
        "average_score": score
    })
