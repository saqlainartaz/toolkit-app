from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session
from functools import wraps
from cs50 import SQL


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


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    if session.get("user_id") is not None:
        return redirect("/")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Please input username!")
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Please input password!")
            return render_template("login.html")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?",
                          request.form.get("username").upper())

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Invalid Creditionals")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if session.get("user_id") is not None:
        return redirect("/")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Must provide new username")
            return render_template("register.html")

        # Ensure password was submitted
        if not request.form.get("password"):
            flash("Must provide new password")
            return render_template("register.html")

        # Ensure confirmation was submitted
        if not request.form.get("confirmation"):
            flash("Must provide new confirmation")
            return render_template("register.html")

        # Ensure password is of desired length
        if len(request.form.get("password")) < 8 or len(request.form.get("password")) > 15:
            flash("Password must be in range of 8-15")
            return render_template("register.html")

        # Ensure the password do Match
        if request.form.get("confirmation") != request.form.get("password"):
            flash("Passwords Do not Match")
            return render_template("register.html")

        usrname = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username").upper())
        # Ensure the username is not already taken
        if len(usrname) != 0:
            flash("Username Taken!")
            return render_template("register.html")

        # Query database for username
        rows = db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", request.form.get(
            "username").upper(), generate_password_hash(request.form.get("password")))

        # Remember which user has logged in
        session["user_id"] = rows

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
