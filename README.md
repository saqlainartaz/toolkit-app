# ToolKit4U

> A Flask web application providing a suite of optimized tools for secure messaging, text readability analysis, credit card validation, and change calculation.

## Features

### Secure Messaging Vault
Store and retrieve notes anonymously — no sender or receiver data is logged. Each note is protected by two layers of access control:
- **Unique access code** — a user-defined identifier for the note
- **Password** — hashed with `werkzeug.security` before storage

### Readability Analyzer
Computes the approximate US grade level of any text using the [Coleman–Liau formula](https://en.wikipedia.org/wiki/Coleman%E2%80%93Liau_index):

```
index = 0.0588 × L - 0.296 × S - 15.8
```

Where `L` is the average number of letters per 100 words and `S` is the average number of sentences per 100 words. Results range from *Before Grade 1* to *Grade 16+*.

### Credit Card Validator
Validates card numbers against Luhn's algorithm and identifies whether the card is a valid **Visa**, **MasterCard**, or **American Express**.

### Change Calculator
Determines the minimum number of coins (quarters, dimes, nickels, pennies) needed for a given dollar amount.

---

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the app:
   ```bash
   flask run
   ```

3. Open `http://127.0.0.1:5000` and register an account.

---

## Tech Stack

| Layer     | Technology                        |
|-----------|-----------------------------------|
| Backend   | Python, Flask, Flask-Session       |
| Database  | SQLite via `cs50.sql`              |
| Frontend  | Jinja2, Bootstrap 5, Bootswatch    |
| Security  | `werkzeug` password hashing        |

## Project Structure

```
app.py              # Flask application — all routes + business logic
mydatabase.db       # SQLite database (users, user_notes)
requirements.txt    # Python dependencies
static/             # CSS, favicons, assets
templates/          # Jinja2 layout files and page templates
```

## Database

| Table        | Key Columns                                          |
|--------------|------------------------------------------------------|
| `users`      | `id`, `username` (stored uppercase), `hash`          |
| `user_notes` | `access` (unique code), `hash`, `title`, `note`, `timestamp` |

## Author

Saqlain Alam — [saqlainartaz](https://github.com/saqlainartaz) · CS50x 2022 Final Project
