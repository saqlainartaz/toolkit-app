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
