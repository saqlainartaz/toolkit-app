# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ToolKit4U is a Flask web application built with Python, HTML, Bootstrap, and JavaScript. It was created as a final project for CS50 2022. The app provides a suite of tools: a secure messaging/vault system, readability analyzer, credit card validator, and change calculator.

## Development Commands

**Install dependencies:**
```
pip install -r requirements.txt
```

**Run the app:**
```
python app.py
```
Then open `http://localhost:5000` in a browser.

**Dependencies** (requirements.txt): `cs50`, `Flask`, `Flask-Session`, `requests`

## Architecture

### Tech Stack
- **Backend:** Flask with Flask-Session for server-side sessions
- **Database:** SQLite (`mydatabase.db`) via the `cs50` SQL wrapper
- **Frontend:** Jinja2 templates, Bootstrap 5.1.3 with Bootswatch Morph theme
- **Password hashing:** `werkzeug.security` (`generate_password_hash` / `check_password_hash`)

### Database Schema
SQLite database at `mydatabase.db` with two tables:
- **users** — `id`, `username` (stored uppercase), `hash`
- **user_notes** — `access` (unique access code), `hash` (note password), `title`, `note`, `timestamp`

Note: `sqlite3` CLI is not installed on this machine. To inspect the database, use Python:
```python
from cs50 import SQL
db = SQL("sqlite:///mydatabase.db")
db.execute("SELECT sql FROM sqlite_master WHERE type='table'")
```

### Route Structure (`app.py`)
All routes except `/login` and `/register` require login via the `@login_required` decorator.

| Route | Methods | Description |
|-------|---------|-------------|
| `/` | GET | Homepage (index) |
| `/login` | GET, POST | User login |
| `/register` | GET, POST | User registration (username uppercased before storage) |
| `/logout` | GET | Clears session, redirects to `/` |
| `/message` | GET, POST | Send/save a message (vault) — creates a note with access code + password |
| `/message2` | GET, POST | Receive/read a message — retrieves note by access code + password |
| `/read` | GET, POST | Readability analyzer using the Coleman-Liau formula |
| `/cash` | GET, POST | Change generator (minimum coins for a dollar amount) |
| `/credit` | GET, POST | Credit card validator (Luhn's algorithm for Amex, MasterCard, Visa) |
| `/password` | GET, POST | Change account password |
| `/about` | GET | About page |
| `/guide` | GET | Messaging guide |

### Key Patterns
- **Login guard:** `@login_required` decorator in `app.py:9-20` checks `session["user_id"]`
- **Flash messages:** Used across all routes for validation feedback
- **Template inheritance:** `layout.html` is the base template; all feature pages extend it via `{% block main %}` and `{% block title %}`
- **No data caching:** `@app.after_request` handler disables browser caching
- **Username handling:** All usernames are stored as uppercased (`.upper()` at login and register)

### File Structure
```
app.py                    # Single-file Flask backend with all routes and logic
mydatabase.db             # SQLite database
requirements.txt          # Python dependencies
static/styles.css         # Custom styles
templates/                # Jinja2 templates (layout.html base, one per feature)
```
