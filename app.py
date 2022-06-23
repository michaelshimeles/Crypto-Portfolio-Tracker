from cProfile import run
from crypt import crypt
import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, usd
from pycoingecko import CoinGeckoAPI

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///crypto.db")

# Configure CoinGeckoAPI
cg = CoinGeckoAPI()


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    
    crypto_portfolio = db.execute("SELECT * FROM crypto_portfolio WHERE user_id = ?", session["user_id"])

    total_value = db.execute("SELECT SUM(total_amount) FROM crypto_portfolio WHERE user_id = ?", session["user_id"])
    total_value = total_value[0]['SUM(total_amount)']
    
    return render_template("index.html", crypto_portfolio=crypto_portfolio, total_value=total_value)


@app.route("/price", methods=["GET", "POST"])
@login_required
def price():
    if request.method == "POST":
        crypto = request.form.get("crypto").lower()

        # Check if crypto is valid
        # coinlist = cg.get_coins_list().lower() <- come back to this

        coin_price = cg.get_price(crypto, vs_currencies='usd')
        final_price = coin_price[crypto]["usd"]

        return render_template("price.html", final_price=final_price)

    else:
        return render_template("price.html")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "POST":

        crypto = request.form.get("crypto").lower()
        amount = request.form.get("amount")

        coin_price = cg.get_price(crypto, vs_currencies='usd')
        final_price = coin_price[crypto]["usd"]

        if not request.form.get("crypto"):
            return apology("You must provide a crypto", 400)

        if not request.form.get("amount"):
            return apology("You must provide an amount", 400)

        # Add transaction to database
        db.execute("INSERT INTO crypto_txs (user_id, tx_type, crypto, num_of_coins, price_per_coin, total_amount_tx, timestamp) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)", session["user_id"], "buy", crypto, amount, final_price, final_price * int(amount))

        
        # Select all info on user's portfolio
        crypto_portfolio = db.execute("SELECT * FROM crypto_portfolio WHERE user_id = ? AND crypto = ?", session["user_id"], crypto)

        if crypto_portfolio == []:
            # Insert stock into stock_folio
            crypto_portfolio = db.execute("INSERT INTO crypto_portfolio (user_id, crypto, num_of_coins, price_per_coin, total_amount) VALUES (?, ?, ?, ?, ?)", session["user_id"], crypto, amount, final_price, final_price * int(amount))
        else:
            # Update stock_folio
            crypto_portfolio = db.execute("UPDATE crypto_portfolio SET num_of_coins = num_of_coins + ? WHERE user_id = ? AND crypto = ?", int(amount), session["user_id"], crypto)
        
        return redirect("/")
    
    else:
        return render_template("buy.html")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method == "GET":
        portfolio = db.execute("SELECT * FROM crypto_portfolio WHERE user_id = ?", session["user_id"])
        return render_template("sell.html", portfolio=portfolio)

    elif request.method == "POST":
        crypto_name = request.form.get("crypto")
        amount = request.form.get("amount")

        if not request.form.get("crypto"):
            return apology("You must provide a crypto", 400)
            
        elif not request.form.get("amount"):
            return apology("You must provide an amount", 400)
        
        if int(amount) < 0:
            return apology("You must provide a positive amount", 400)

        user_coins = db.execute("SELECT num_of_coins FROM crypto_portfolio WHERE user_id = ? AND crypto = ?", session["user_id"], crypto_name)

        if int(amount) > int(user_coins[0]["num_of_coins"]):
            return apology("You don't have that many coins", 400)

        coin_price = cg.get_price(crypto_name, vs_currencies='usd')
        final_price = coin_price[crypto_name]["usd"]
        
        # Add transaction to database
        add_tx = db.execute("INSERT INTO crypto_txs (user_id, tx_type, crypto, num_of_coins, price_per_coin, total_amount_tx, timestamp) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)", session["user_id"], "sell", crypto_name, amount, final_price, final_price * int(amount))

        # Update user's portfolio
        update_portfolio = db.execute("UPDATE crypto_portfolio SET num_of_coins = num_of_coins - ? WHERE user_id = ? AND crypto = ?", int(amount), session["user_id"], crypto_name)

        # remove crypto from portfolio if user has no coins
        if int(user_coins[0]["num_of_coins"]) - int(amount) == 0:
            db.execute("DELETE FROM crypto_portfolio WHERE user_id = ? AND crypto = ?", session["user_id"], crypto_name)

        return redirect("/")
    
@app.route("/history")
@login_required
def history():
    if request.method == "GET":
        txs = db.execute("SELECT * FROM crypto_txs WHERE user_id = ?", session["user_id"])
        return render_template("history.html", txs=txs)

@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 400)

        if not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        userInfo = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(userInfo) != 1 or not check_password_hash(userInfo[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = userInfo[0]["id"]

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        if not request.form.get("firstname"):
            return apology("must provide first name", 400)

        elif not request.form.get("lastname"):
            return apology("must provide last name", 400)

        elif not request.form.get("username"):
            return apology("must provide username", 400)

        elif not request.form.get("password"):
            return apology("must provide password", 400)

        if request.form.get("password") != request.form.get("confirmation"):
            return apology("Password does not match", 400)

        # Query database for username
        checkUsername = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username is not already taken
        if len(checkUsername) != 0:
            return apology("Username already exists", 400)

        # Store username and password in database
        userInfo = db.execute("INSERT INTO users (username, firstname, lastname, hash) VALUES(?, ?, ?, ?)", request.form.get(
            "username"), request.form.get("firstname"), request.form.get("lastname"), generate_password_hash(request.form.get("password")))

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("register.html")
