from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session
from functools import wraps
from cs50 import SQL
import datetime


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///mydatabase.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show Homepage"""
    return render_template("index.html")


@app.route("/message", methods=["GET", "POST"])
@login_required
def message():
    """ Saves messsage to database """

    if request.method == "POST":

        access = request.form.get("access")
        password = request.form.get("password")
        title = request.form.get("title")
        note = request.form.get("note")

        if not access:
            flash("Title cannot be left empty!")
            return render_template("send.html")

        if not password:
            flash("Must provide new password")
            return render_template("send.html")

        if not note:
            flash("Title cannot be left empty!")
            return render_template("send.html")

        date = datetime.datetime.now()

        if len(request.form.get("password")) < 8 or len(request.form.get("password")) > 15:
            flash("Password must be in range of 8-15")
            return render_template("send.html")

        access_code = db.execute(
            "SELECT * FROM user_notes WHERE access=?", access)

        if len(access_code) != 0:
            flash("Error with access code, Try again!")
            return render_template("send.html")

        db.execute("INSERT INTO user_notes (access, hash, title, note, timestamp) VALUES(?, ?, ?, ?, ?)",
                   access, generate_password_hash(password), title, note, date)

        flash("Note Saved Successfully!")

        return render_template("password2.html", access=access, password=password)

    else:
        return render_template("send.html")


@app.route("/message2", methods=["GET", "POST"])
@login_required
def message2():

    if request.method == "POST":

        access = request.form.get("access")
        password = request.form.get("password")

        if not access:
            flash("Please input access code!")
            return render_template("recieve.html")

        if not password:
            flash("Must provide new password")
            return render_template("recieve.html")

        rows = db.execute("SELECT * FROM user_notes WHERE access = ?",
                          access)

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            flash("Invalid Note Access Creditionals!")
            return render_template("recieve.html")

        dataset = db.execute(
            "SELECT title, note, timestamp FROM user_notes WHERE access=?", access)

        database = []

        for row in dataset:
            title = row["title"]
            note = row["note"]
            timestamp = row["timestamp"]
            database.append(
                {"title": title, "note": note, "timestamp": timestamp})

        flash("Message Recieved Successfully")

        return render_template("recieved.html", database=database)

    else:
        return render_template("recieve.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    if session.get("user_id") is not None:
        return redirect("/")

    if request.method == "POST":

        if not request.form.get("username"):
            flash("Please input username!")
            return render_template("login.html")

        elif not request.form.get("password"):
            flash("Please input password!")
            return render_template("login.html")

        rows = db.execute("SELECT * FROM users WHERE username = ?",
                          request.form.get("username").upper())

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Invalid Creditionals")
            return render_template("login.html")

        session["user_id"] = rows[0]["id"]

        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    session.clear()

    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if session.get("user_id") is not None:
        return redirect("/")

    if request.method == "POST":

        if not request.form.get("username"):
            flash("Must provide new username")
            return render_template("register.html")

        if not request.form.get("password"):
            flash("Must provide new password")
            return render_template("register.html")

        if not request.form.get("confirmation"):
            flash("Must provide new confirmation")
            return render_template("register.html")

        if len(request.form.get("password")) < 8 or len(request.form.get("password")) > 15:
            flash("Password must be in range of 8-15")
            return render_template("register.html")

        if request.form.get("confirmation") != request.form.get("password"):
            flash("Passwords Do not Match")
            return render_template("register.html")

        usrname = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username").upper())
        if len(usrname) != 0:
            flash("Username Taken!")
            return render_template("register.html")

        rows = db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", request.form.get(
            "username").upper(), generate_password_hash(request.form.get("password")))

        session["user_id"] = rows

        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/cash", methods=["GET", "POST"])
@login_required
def cash():
    if request.method == "POST":

        try:
            cents = float(request.form.get("cash"))
        except:
            flash("Please input a valid value!")
            return render_template("cash.html")

        if cents < 0.1:
            flash("Please input a valid value!")
            return render_template("cash.html")

        cents = cents * 100

        quarters = cents / 25
        quarters = int(quarters)

        cents = cents - quarters * 25

        dimes = cents / 10
        dimes = int(dimes)

        cents = cents - dimes * 10

        nickels = cents / 5
        nickels = int(nickels)

        cents = cents - nickels * 5

        pennies = cents / 1
        pennies = int(pennies)

        coins = quarters + dimes + nickels + pennies

        return render_template("cashed.html", quarters=quarters, dimes=dimes, nickels=nickels, pennies=pennies, coins=coins)
    else:
        return render_template("cash.html")


@app.route("/credit", methods=["GET", "POST"])
@login_required
def credit():

    if request.method == "GET":
        return render_template("credit.html")

    else:
        try:
            card = int(request.form.get("card"))
        except:
            flash("Please don't mess around!")
            return render_template("credit.html")

        d2 = int((card % 100) / 10) * 2
        d4 = int((card % 10000) / 1000) * 2
        d6 = int((card % 1000000) / 100000) * 2
        d8 = int((card % 100000000) / 10000000) * 2
        d10 = int((card % 10000000000) / 1000000000) * 2
        d12 = int((card % 1000000000000) / 100000000000) * 2
        d14 = int((card % 100000000000000) / 10000000000000) * 2
        d16 = int((card % 10000000000000000) / 1000000000000000) * 2

        d1 = card % 10
        d3 = int((card % 1000) / 100)
        d5 = int((card % 100000) / 10000)
        d7 = int((card % 10000000) / 1000000)
        d9 = int((card % 1000000000) / 100000000)
        d11 = int((card % 100000000000) / 10000000000)
        d13 = int((card % 10000000000000) / 1000000000000)
        d15 = int((card % 1000000000000000) / 100000000000000)

        d2 = (d2 % 10) + int((d2 % 100) / 10)
        d4 = (d4 % 10) + int((d4 % 100) / 10)
        d6 = (d6 % 10) + int((d6 % 100) / 10)
        d8 = (d8 % 10) + int((d8 % 100) / 10)
        d10 = (d10 % 10) + int((d10 % 100) / 10)
        d12 = (d12 % 10) + int((d12 % 100) / 10)
        d14 = (d14 % 10) + int((d14 % 100) / 10)
        d16 = (d16 % 10) + int((d16 % 100) / 10)

        sum1 = d2 + d4 + d6 + d8 + d10 + d12 + d14 + d16

        sum2 = d1 + d3 + d5 + d7 + d9 + d11 + d13 + d15

        totalSum = sum1 + sum2

        amex = int(card / 10000000000000)

        master = int(card / 100000000000000)

        visa1 = int(card / 1000000000000)

        visa2 = int(card / 1000000000000000)

        if totalSum % 10 != 0:
            response = "This Card is Invalid!"
            return render_template("credited.html", response=response)

        if amex == 34 or amex == 37:
            response = "This is a valid AMEX Card!"
            return render_template("credited.html", response=response)

        if master == 51 or master == 52 or master == 52 or master == 53 or master == 54 or master == 55:
            response = "This is a valid MASTERCARD!"
            return render_template("credited.html", response=response)

        if visa1 == 4 or visa2 == 4:
            response = "This is a valid VISA Card!"
            return render_template("credited.html", response=response)

        else:
            response = "This Card is Invalid!"
            return render_template("credited.html", response=response)


@app.route("/read", methods=["GET", "POST"])
@login_required
def read():

    if request.method == "POST":
        text = request.form.get("input")

        if not text:
            flash("Please input text to be assessed!")
            return render_template("read.html")

        letters = 0
        for rows in text:
            if rows.isalpha():
                letters = letters + 1

        words = 1
        for rows in text:
            if rows.isspace():
                words = words + 1

        sentences = 0
        for rows in text:
            if rows in [".", "!", "?"]:
                sentences = sentences + 1

        averageLetters = (letters * 100) / words

        averageSentences = (sentences * 100) / words

        index = round((0.0588 * averageLetters) - (0.296 * averageSentences) - 15.8)

        if index >= 16:
            index = "Grade 16+"
            return render_template("read_result.html", index=index)
        elif index < 1:
            index = "Before Grade 1"
            return render_template("read_result.html", index=index)
        else:
            index = f"Grade {index}"
            return render_template("read_result.html", index=index)
    else:
        return render_template("read.html")
