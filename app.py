import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import itertools
import requests

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required
import re

# Configure application
app = Flask(__name__)

# Creates the database variable
db = SQL("sqlite:///final.db")

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    # Brings the user to the home page and displays posts

    # Gets all of the Postids from the posts database
    index = db.execute("SELECT Postid FROM posts")

    # Loops through all of the posts
    for i in index:

        # Gets the liked and disliked columns from votes and stores them in 2 separate variables
        disliked = (db.execute("SELECT disliked FROM votes WHERE post_id = ? AND user_id = ?", i['Postid'], session['user_id']))
        liked = db.execute("SELECT liked FROM votes WHERE post_id = ? AND user_id = ?", i['Postid'], session['user_id'])

        # If either variable is empty, creates the entry for that post for that user
        if disliked == [] or liked == []:
            db.execute("INSERT INTO votes (post_id, user_id) VALUES (?, ?)", i['Postid'], session["user_id"])

        # If the user interacts with the website via POST
        if request.method == 'POST':

            # Adds a dislike to the specific post
            if request.form.get('dislike' + str(i['Postid'])) == 'DISLIKE' and disliked[0]['disliked'] == 0 and liked[0]['liked'] == 0:
                # Updates the database to reflect the new dislike
                dislikes = int((db.execute("SELECT dislikes FROM posts WHERE Postid = ?", i['Postid']))[0]['dislikes']) + 1
                db.execute("UPDATE posts SET dislikes = ? WHERE Postid = ?", dislikes, i['Postid'])

                # Limits the user to only 1 dislike
                db.execute("UPDATE votes SET disliked = ? WHERE post_id = ? AND user_id = ?", 1, i['Postid'], session["user_id"])

            # If the dislike button is clicked and the liked button has already been clicked, switches from liked to disliked
            if request.form.get('dislike' + str(i['Postid'])) == 'DISLIKE' and disliked[0]['disliked'] == 0 and liked[0]['liked'] == 1:
                # Adds a dislikes to the database
                dislikes = int((db.execute("SELECT dislikes FROM posts WHERE Postid = ?", i['Postid']))[0]['dislikes']) + 1
                db.execute("UPDATE posts SET dislikes = ? WHERE Postid = ?", dislikes, i['Postid'])

                # Removes a like from the database to account for the switch
                likes = int((db.execute("SELECT likes FROM posts WHERE Postid = ?", i['Postid']))[0]['likes'])
                db.execute("UPDATE posts SET likes = ? WHERE Postid = ?", likes - 1, i['Postid'])

                # Limits the user to only 1 dislike and switches choice from liked to disliked
                db.execute("UPDATE votes SET disliked = ? WHERE post_id = ? AND user_id = ?", 1, i['Postid'], session["user_id"])
                db.execute("UPDATE votes SET liked = ? WHERE post_id = ? AND user_id = ?", 0, i['Postid'], session["user_id"])

            # If the disliked button has already been clicked and the user clicks it again, removes the dislike
            if request.form.get('dislike' + str(i['Postid'])) == 'DISLIKE' and disliked[0]['disliked'] == 1 and liked[0]['liked'] == 0:
                # Updates the database to remove the dislike
                dislikes = int((db.execute("SELECT dislikes FROM posts WHERE Postid = ?", i['Postid']))[0]['dislikes'])
                db.execute("UPDATE posts SET dislikes = ? WHERE Postid = ?", dislikes - 1, i['Postid'])

                # Changes the status of disliked or not in votes so the GUI updates
                db.execute("UPDATE votes SET disliked = ? WHERE post_id = ? AND user_id = ?", 0, i['Postid'], session["user_id"])
                print(i['Postid'])

            # Adds a like to the specific post
            if request.form.get('like' + str(i['Postid'])) == 'LIKE' and liked[0]['liked'] == 0 and disliked[0]['disliked'] == 0:
                # Updates the likes in the database to account for the new like
                likes = int((db.execute("SELECT likes FROM posts WHERE Postid = ?", i['Postid']))[0]['likes']) + 1
                db.execute("UPDATE posts SET likes = ? WHERE Postid = ?", likes, i['Postid'])

                # Limits the user to only 1 like
                db.execute("UPDATE votes SET liked = ? WHERE post_id = ? AND user_id = ?", 1, i['Postid'], session["user_id"])

            # Switches from a dislike to a like
            if request.form.get('like' + str(i['Postid'])) == 'LIKE' and liked[0]['liked'] == 0 and disliked[0]['disliked'] == 1:
                # Accounts for the change to a like by updating the likes column
                likes = int((db.execute("SELECT likes FROM posts WHERE Postid = ?", i['Postid']))[0]['likes']) + 1
                db.execute("UPDATE posts SET likes = ? WHERE Postid = ?", likes, i['Postid'])

                # Updates the dislike column to account for the switch from a dislike to a like
                dislikes = int((db.execute("SELECT dislikes FROM posts WHERE Postid = ?", i['Postid']))[0]['dislikes'])
                db.execute("UPDATE posts SET dislikes = ? WHERE Postid = ?", dislikes - 1, i['Postid'])

                # Limits the user to only 1 like
                db.execute("UPDATE votes SET liked = ? WHERE post_id = ? AND user_id = ?", 1, i['Postid'], session["user_id"])
                db.execute("UPDATE votes SET disliked = ? WHERE post_id = ? AND user_id = ?", 0, i['Postid'], session["user_id"])

            # If the liked button was already clicked and the user clicks it again, unlikes the post
            if request.form.get('like' + str(i['Postid'])) == 'LIKE' and liked[0]['liked'] == 1 and disliked[0]['disliked'] == 0:
                # Updates the likes column to reflect unliking the post
                likes = int((db.execute("SELECT likes FROM posts WHERE Postid = ?", i['Postid']))[0]['likes'])
                db.execute("UPDATE posts SET likes = ? WHERE Postid = ?", likes - 1, i['Postid'])

                # Resets the liked column so that a user can like the post again
                db.execute("UPDATE votes SET liked = ? WHERE post_id = ? AND user_id = ?", 0, i['Postid'], session["user_id"])


            # If the name of the commentHere button matches "commentHereButton" + i, adds a comment to the database
            if request.form.get('commentHereButton' + str(i['Postid'])) == "COMMENT":
                # Creates the comments table if not already existing
                db.execute("CREATE TABLE IF NOT EXISTS comments (comment_id int IDENTITY(1, 1) PRIMARY KEY, post_id int, user_id int, message TEXT, FOREIGN KEY (user_id) REFERENCES users(id), FOREIGN KEY (post_id) REFERENCES posts(Postid))")

                # Gets the latest comment ID from comments
                numOfComments = db.execute("SELECT comment_id FROM comments ORDER BY comment_id DESC LIMIT 1")

                # If no value is in the comments table, sets the value of numOfComments to 1 to indicate it is the first comment
                if numOfComments == []:
                    numOfComments = 1
                # If the value is not empty (is a number), then it increases the latest comment ID by 1
                else:
                    numOfComments = db.execute("SELECT comment_id FROM comments ORDER BY comment_id DESC LIMIT 1")[0]['comment_id'] + 1

                # Ensures the user has a comment when they click the comment button
                if not request.form.get("commentBox" + str(i['Postid'])):
                    return apology("must input a message", 400)

                # Gets the message the user input in the specific comment box
                message = request.form.get("commentBox" + str(i['Postid']))

                # Inserts the relevant information into the comments table for a single comment
                db.execute("INSERT INTO comments (comment_id, post_id, user_id, message) VALUES (?, ?, ?, ?)", numOfComments, i['Postid'], session['user_id'], message)

    # Gets all of the information that the post will need to display for every post
    info = db.execute("SELECT * FROM posts")

    # Creates comment variable
    comment = db.execute("SELECT * FROM comments")

    # Gets the votes from the user that is logged in (since that is all that will be needed for the html page display)
    vote = db.execute("SELECT * FROM votes WHERE user_id = ?", session["user_id"])

    # Returns the home page with all of the posts
    return render_template("home.html", postInfo=info, comments=comment, votes=vote)


@app.route("/register", methods=["GET", "POST"])
def register():
    # Register user

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # https://www.c-sharpcorner.com/article/how-to-validate-an-email-address-in-python/#:~:text=Validating%20an%20Email%20Address%20in%20Python%201%20import,8%20if%20__name__%20%3D%3D%20%27__main__%27%20%3A%20More%20items
        # Using this code as reference to verify email addresses exist
        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'

        # Sets email equal to the text the user input in the email box
        email = request.form.get("email")

        # Checks if the email is valid otherwise returns an error
        if(re.search(regex,email)):
            print("Valid Email")
        else:
            return apology("invalid email", 400)

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensures username is not a duplicate
        if request.form.get("username") in db.execute("SELECT username FROM users"):
            return apology("username already exists", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm password", 400)

        # Ensures passwords match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords must match", 400)

        # Inserts the username and hash of the password into the users database
        db.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                   request.form.get("username"), generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8), request.form.get("email"))

        # Accounts for the user deleting a column in the users database since it autoincrements
        users = db.execute("SELECT id FROM users ORDER BY id DESC limit 2")
        incorrectID = users[0]['id']
        nowCorrect = incorrectID
        prevID = users[1]['id']
        if (incorrectID - prevID) != 1:
            nowCorrect = prevID + 1

        # Updates the column to reflect the appropriate id
        db.execute("UPDATE users SET id = ? WHERE username = ?", nowCorrect, request.form.get("username"))

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # Logs user in

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Gets all of the Postids from the posts database
        index = db.execute("SELECT Postid FROM posts")

        # Loops through all of the posts
        for i in index:

            # Gets the liked and disliked columns from votes and stores them in 2 separate variables
            disliked = (db.execute("SELECT disliked FROM votes WHERE post_id = ? AND user_id = ?", i['Postid'], session['user_id']))
            liked = db.execute("SELECT liked FROM votes WHERE post_id = ? AND user_id = ?", i['Postid'], session['user_id'])

            # If either variable is empty, creates the entry for that post for that user
            if disliked == [] or liked == []:
                db.execute("INSERT INTO votes (post_id, user_id) VALUES (?, ?)", i['Postid'], session["user_id"])

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Brings the user to the login page
        return render_template("login.html")


@app.route("/logout")
def logout():
    # Logs the user out

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/profile")
def profile():
    # Goes to the user's profile

    # Gets the username of the currently logged in user
    user = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
    user = user[0]['username']

    # Returns profile.html with the username being equal to the user's name
    info = db.execute("SELECT * FROM posts WHERE username = ?", user)
    return render_template("profile.html", postInfo=info, username=user)


@app.route("/newPost", methods=["GET", "POST"])
def newPost():
    # Makes a new post

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # If there is no title, throws an error
        if not request.form.get("postTitle"):
            return apology("must provide title", 400)

        # If there is no message, returns an error
        if not request.form.get("message"):
            return apology("must provide message", 400)

        # Creates the posts table if it does not exist
        db.execute("CREATE TABLE IF NOT EXISTS posts (Postid int IDENTITY(1,1) PRIMARY KEY, user_id int, title text, message text, date text, likes DEFAULT 0, dislikes DEFAULT 0, username text, FOREIGN KEY (user_id) REFERENCES users(id))")

        # Checks if there is a title that matches the current title the user input
        duplicateTitle = db.execute("SELECT title FROM posts WHERE title = ? AND user_id = ?", request.form.get("postTitle"), session["user_id"])

        # If there is a duplicate title, returns error message
        if duplicateTitle != []:
            return apology("can't use the same post title", 400)

        # Gets the current date
        date = datetime.now().date()

        # Gets the title of the post from the input field
        title = request.form.get("postTitle")

        # Gets the post from the input field
        message = request.form.get("message")

        # Gets the latest Postid from posts
        numOfPosts = db.execute("SELECT Postid FROM posts ORDER BY Postid DESC LIMIT 1")
        # If no value is in the posts table, sets the value of numOfPosts to 1 to indicate it is the first post
        if numOfPosts == []:
            numOfPosts = 1
        # If the value is not empty (is a number), then it increases the latest Postid by 1
        else:
            numOfPosts = db.execute("SELECT Postid FROM posts ORDER BY Postid DESC LIMIT 1")[0]['Postid'] + 1

        # Gets the name of the user
        name = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])

        # Inserts info into Postid, user_id, title, message, date, and username columns
        db.execute("INSERT INTO posts (Postid, user_id, title, message, date, username) VALUES (?, ?, ?, ?, ?, ?)",
                   numOfPosts, session["user_id"], title, message, date, name[0]["username"])

        # Creates the votes table for later use
        db.execute("CREATE TABLE IF NOT EXISTS votes (post_id int, user_id int, liked BOOLEAN DEFAULT false, disliked BOOLEAN DEFAULT false)")

        # Redirects the user to the home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # brings the user to the makepost page
        return render_template("makepost.html")

