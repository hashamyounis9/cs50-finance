import os
import re
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, send_file
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# homepage of our webapp
@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # getting batabase contents to display
    record_of_current_user = db.execute(
        "SELECT id, symbol, SUM(shares) FROM history WHERE id = ? GROUP BY symbol HAVING SUM(shares) > 0 ORDER BY price DESC", session["user_id"])

    cash = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

    # update record of current user with stock current price and total actual price of shares
    current_worth = 0
    for stock in record_of_current_user:
        stock_data = lookup(stock["symbol"])
        stock["currentprice"] = stock_data["price"]
        stock["totalprice"] = stock_data["price"] * stock["SUM(shares)"]
        current_worth += stock["totalprice"]
    return render_template("index.html", record_of_current_user=record_of_current_user, cash=cash, current_worth=current_worth)

# a route that allows users to buy stocks if they can afford


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # if request method is POST, it means user input is to be processed
    if request.method == "POST":
        # extracting user input from the html document
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        stock = lookup(symbol)

        # validating user input
        if symbol == "" or shares == "":
            return apology("Symbol or shares field can't be empty", 400)
        if not stock:
            return apology("Invalid Symbol", 400)
        if not shares.isnumeric():
            return apology("shares should be numeric", 400)
        if float(shares) <= 0:
            return apology("Invalid shares value", 400)

        # collecting more needed data to process
        record_of_current_user = db.execute(
            "SELECT * FROM users where id = ?", session["user_id"])
        cash = record_of_current_user[0]["cash"]
        price = stock["price"]
        total_price = float(price) * float(shares)
        if total_price > cash:
            return apology("Can't afford", 400)
        else:
            # add transaction details to history table in db
            db.execute("INSERT INTO history(id, symbol, shares, price) VALUES(?, ?, ?, ?)",
                       session["user_id"],
                       stock["symbol"],
                       float(shares),
                       stock["price"]
                       )
            # update cash of user after buying stocks
            db.execute("UPDATE users SET cash = ? WHERE id = ?",
                       float(cash) - float(total_price),
                       session["user_id"]
                       )
            # getting users data before purchase to calculate amounts after purchase
            record_of_current_user = db.execute(
                "SELECT SUM(shares) FROM history where id = ?", session["user_id"])

            total_shares = record_of_current_user[0]["SUM(shares)"] + \
                float(shares)

            # updating users portfolio
            db.execute("INSERT INTO portfolio(id, symbol, shares) VALUES (?, ?, ?)",
                       session["user_id"], stock["symbol"], total_shares)

            # displaying notification that purchase was success
            flash("Bought!")

        # after completing transaction, redirect user to homepage
        return redirect("/")

    # if request method is not POST(etc. GET), it means need to display html document
    else:
        return render_template("buy.html")


# page/route for dislaying uesrs history of purchases and sales
@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # getting contents of database
    record_of_current_user = db.execute(
        "SELECT * FROM history WHERE id = ?", session["user_id"])

    # rendering dayabase contents using html page
    return render_template("history.html", record_of_current_user=record_of_current_user)


# route to let users log in
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get(
                "username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


# route to let users log out
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


# route for checking price of stocks
@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # process user data if request method is post
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("invalid input", 400)

        stock = lookup(symbol)

        if not stock:
            return apology("Invalid Stock symbol", 400)
        else:
            name = stock["symbol"]
            price = stock["price"]
            return render_template("quoted.html", name=name, price=usd(price))
    # display html page if request is not get
    else:
        return render_template("quote.html")


# route to let new users register
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    session.clear()

    # process users data if request method is post
    if request.method == "POST":
        # extract users input from html page using element names
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if email is None:
            email = username + "@gmail.com"

        # method to define and validate email format
        def is_valid_gmail(email):
            email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@gmail.com')
            match = email_pattern.match(email)
            return bool(match)

        # validate users input
        if not (is_valid_gmail(email)):
            return apology("invalid email format", 400)

        # checking if email is already linked to another account
        check_db = db.execute("SELECT * FROM users WHERE email = ?", email)
        if len(check_db) != 0:
            return apology("Email is already linked with another account, try again with different email", 400)

        # validate input
        if not (password == confirmation):
            return apology("Passwords should be same", 400)

        if username == "" or password == "" or confirmation == "":
            return apology("All inputs are required", 400)

        rows = db.execute("SELECT * FROM users WHERE username=?", username)
        if len(rows) == 1:
            return apology("username already taken, try another one", 400)

        # update DB with user input
        else:
            db.execute("INSERT INTO users (username, hash, email) VALUES(?, ?, ?)",
                       username, generate_password_hash(password), email)

        # notification for registration
        flash("Account registered Successfully!")
        return redirect("/")
    else:
        return render_template("register.html")


# route to let users sell their stocks
@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    # process user data if request method is post
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        # validate user input
        if symbol == "":
            return apology("Invalid symbol", 400)
        if not shares.isnumeric() or shares == "" or int(shares) <= 0:
            return apology("Invalid shares", 400)

        stock = lookup(symbol)

        if not stock:
            return apology("Invalid symbol", 400)

        # get contents of DB if user have shares so they can sell the shares
        record_of_current_user = db.execute(
            "SELECT id, symbol, SUM(shares) FROM history WHERE id = ? AND symbol = ? GROUP BY symbol HAVING SUM(shares) > 0", session["user_id"], stock["symbol"])

        cash = db.execute("SELECT * FROM users WHERE id = ?",
                          session["user_id"])
        # does user have enough shares to sell
        if record_of_current_user[0]["SUM(shares)"] < int(shares):
            return apology("You don't own that much shares", 400)

        # update DB as user can the shares
        else:
            selling_for = stock["price"] * int(shares)
            current_cash = cash[0]["cash"]
            db.execute("UPDATE users SET cash = ? WHERE id = ?",
                       current_cash + selling_for, session["user_id"])
            db.execute("INSERT INTO history (id, symbol, shares, price) VALUES (?, ?, ?, ?)",
                       session["user_id"], stock["symbol"], -(int(shares)), stock["price"])
            flash("Sold Successfully!")
        return redirect("/")

    # if request method is GET, let user select shares to sell from the share user owns
    else:
        record_of_current_user = db.execute(
            "SELECT id, symbol, SUM(shares) FROM history WHERE id = ? GROUP BY symbol HAVING SUM(shares)>0 ORDER BY symbol", session["user_id"])

        return render_template("sell.html", record_of_current_user=record_of_current_user)


# route to let user reset their password on basis of given email
@app.route("/reset", methods=["GET", "POST"])
def reset():
    """Resetting user's password"""
    # collect user input from html page if request method is post
    if request.method == "POST":
        new_password = request.form.get("password")
        confirmation = request.form.get("confirmpassword")

        # validate new password
        if new_password == "" or confirmation == "" or new_password != confirmation:
            return apology("Invalid passwords, or passwords do not match", 400)

        # update user password
        db.execute("UPDATE users SET hash = ? WHERE email = ?",
                   generate_password_hash(new_password), session["email"])

        # notofocation for password reset success
        flash("Password has been Reset Successfully!")
        return redirect("/login")

    else:
        return render_template("reset.html")

# route to let users allow forget password procedure


@app.route("/forgotpassword", methods=["GET", "POST"])
def forgotpassowrd():
    """Reset user's password if possible"""
    # collect uer input from page if request is POST
    if request.method == "POST":
        email = request.form.get("email")
        # vailidate user input

        def is_valid_gmail(email):
            email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@gmail\.com$')
            match = email_pattern.match(email)
            return bool(match)
        # if invalid email format
        if not (is_valid_gmail(email)):
            return apology("invalid email format", 400)

        # look for users email in DB
        check_db = db.execute("SELECT * FROM users WHERE email = ?", email)

        # if email is not in DB
        if len(check_db) == 0:
            return apology("Email not found in our database", 400)
        # if email is found in database
        flash("Email found in Database!")

        # insert email in session variable so that password of user can be updated on this email's basis in resetpassword route
        session["email"] = email

        # user can now reset password
        return redirect("/reset")

    else:
        return render_template("forgot.html")


# route to let users add more cash to their account
@app.route("/addcash", methods=["GET", "POST"])
@login_required
def addcash():
    """Allow user to add more cash"""

    # collect and process and validate user input from html page
    if request.method == "POST":
        allowed_cash = [10, 100, 1000]
        cash = request.form.get("cash")
        if not cash.isnumeric() or int(cash) not in allowed_cash:
            return apology("Invalid cash input", 400)

        # extract existing cash of user from DB
        check_db = db.execute(
            "SELECT cash FROM users WHERE id = ?", session["user_id"])
        # store current cash in variable
        current_cash = check_db[0]["cash"]

        # add more cash to users account along with existing cash
        db.execute("UPDATE users SET cash = ? WHERE id = ?", int(
            current_cash) + int(cash), session["user_id"])
        # notify for success
        flash("Cash Added!")

        return redirect("/")
    # display page contents if request is not POST(etc. GET)
    else:
        return render_template("addcash.html")
