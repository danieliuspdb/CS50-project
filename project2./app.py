from flask import Flask
import os
import datetime
import json
import string
from pprint import pprint
from datetime import datetime
import atexit
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from helpers import apology, login_required
import websocket, json, pprint, talib, numpy
import os
from binance.client import Client
from binance.enums import *
from threading import *
from multiprocessing import Pool
import multiprocessing as mp
import numpy as np
from celery import Celery
import time
from flask_celery import make_celery
import threading
import contextlib
from sqlalchemy import delete







app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = 'super secret key'

app.config['CELERY_BROKER_URL'] = 'redis://127.0.0.1:5000/'
app.config['CELERY_RESULT_BACKEND'] = 'redis://127.0.0.1:5000/'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
DB_NAME = "database.db"
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    API_KEY1 = db.Column(db.String(200), nullable=False)
    API_KEY2 = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"User('{self.username}')"

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), unique=True, nullable=False)
    pair = db.Column(db.String(60), nullable=False)
    side = db.Column(db.String(200), nullable=False)
    price = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.String(200), nullable=False)
    total = db.Column(db.String(200), nullable=False)

#client = Client(config.API_KEY, config.API_SECRET)

TRADE_SYMBOL = 'ETHEUR'
TRADE_QUANTITY = 0.015

def order(side, quantity, symbol,order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        tmp = User.query.filter_by(id=session["user_id"]).first()
        client = Client(tmp.API_KEY1, tmp.API_KEY2)
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False

    return True


def algo():
    SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"

    RSI_PERIOD = 14
    RSI_OVERBOUGHT = 70
    RSI_OVERSOLD = 30
    TRADE_SYMBOL = 'ETHEUR'
    TRADE_QUANTITY = 0.015

    closes = []
    in_position = False

    tmp = User.query.filter_by(id=session["user_id"]).first()
    client = Client(tmp.API_KEY1, tmp.API_KEY2)

    def order(side, quantity, symbol,order_type=ORDER_TYPE_MARKET):
        try:
            print("sending order")
            tmp = User.query.filter_by(id=session["user_id"]).first()
            client = Client(tmp.API_KEY1, tmp.API_KEY2)
            order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
            print(order)
        except Exception as e:
            print("an exception occured - {}".format(e))
            return False

        return True


    def on_open(ws):
        print('opened connection')

    def on_close(ws):
        print('closed connection')

    def on_message(ws, message):
        #global closes, in_position

        #print('received message')
        json_message = json.loads(message)
        #pprint.pprint(json_message)

        candle = json_message['k']

        is_candle_closed = candle['x']
        close = candle['c']

        if is_candle_closed:
            print("candle closed at {}".format(close))
            closes.append(float(close))
            print("closes")
            print(closes)

            if len(closes) > RSI_PERIOD:
                np_closes = numpy.array(closes)
                rsi = talib.RSI(np_closes, RSI_PERIOD)
                print("all rsis calculated so far")
                print(rsi)
                last_rsi = rsi[-1]
                print("the current rsi is {}".format(last_rsi))

                if last_rsi > RSI_OVERBOUGHT:
                    if in_position:
                        print("Overbought! Sell! Sell! Sell!")
                        # put binance sell logic here
                        order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                        if order_succeeded:
                            in_position = False
                    else:
                        print("It is overbought, but we don't own any. Nothing to do.")

                if last_rsi < RSI_OVERSOLD:
                    if in_position:
                        print("It is oversold, but you already own it, nothing to do.")
                    else:
                        print("Oversold! Buy! Buy! Buy!")
                        # put binance buy order logic here
                        order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                        if order_succeeded:
                            in_position = True


    ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
    ws.run_forever()
a1 = 'asf'
a2 = 'gsfds'

def asl():
    return a1
def asf():
    return a2

#def fir(a):
#    return(a)

#def fir(b):
#    return(b)

@app.route("/buy_sell", methods=["GET", "POST"])
@login_required
def buy_sell():

    if request.method == "POST":
        if request.form['submit_button'] == 'buy':
            print('asfdaf')
            smb = request.form.get("symbol")
            qua = request.form.get("quantity")
            order_succeeded = order(SIDE_BUY, qua, smb)
        elif request.form['submit_button'] == 'sell':
            smb = request.form.get("symbol2")
            qua = request.form.get("quantity2")
            order_succeeded = order(SIDE_SELL, qua, smb)
        return redirect("/history")

    else:
        tmp = User.query.filter_by(id=session["user_id"]).first()
        client = Client(tmp.API_KEY1, tmp.API_KEY2)
        exchange_info = client.get_exchange_info()
        return render_template("buy_sell.html", exchange_info = exchange_info)


@app.route('/bot2', methods=["GET", "POST"])
@login_required
def bot2():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        return redirect("/bot")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("bot.html")

@app.route('/bot', methods=["GET", "POST"])
@login_required
def bot():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        algo()
        return redirect("/bot2")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("index2.html")


@app.route('/')
@login_required
def hello_world():



    return render_template("index.html")


@app.route('/history')
@login_required
def history():

    tmp = User.query.filter_by(id=session["user_id"]).first()
    client = Client(tmp.API_KEY1, tmp.API_KEY2)
    trades = client.get_my_trades(symbol='ETHEUR')

    print(trades)

    def myFunc(e):
        return e['time']

    for i in trades:
        i["price"] = round(float(i["price"]), 2)
        i["qty"] = round(float(i["qty"]), 5)
        i["quoteQty"] = round(float(i["quoteQty"]), 2)
        i["time"] = datetime.fromtimestamp(int(i["time"])/1000)
        i["time"] = i["time"].replace(microsecond=0)
        #if i["time"] == 2:
        #del test_list[i]

    trades.sort(reverse=True, key=myFunc)

    return render_template("history.html", trades = trades)


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
        rows = User.query.filter_by(username=str(request.form.get("username"))).first()

        # Ensure username exists and password is correct
        if rows == None or not check_password_hash(rows.password, request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows.id

        a = User.query.filter_by(id=session["user_id"]).first()

        global a1, a2

        a1 = a.API_KEY1

        a2 = a.API_KEY2

        asl()

        asf()

        client = Client(a1, a2)

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
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Query database for username
        x = str(request.form.get("username"))
        rows = User.query.filter_by(username=x).first()

        # Ensure username is not taken
        if rows != None:
            return apology("username is already taken", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)


        # Ensure password was repeated
        if not request.form.get("confirmation"):
            return apology("must provide password both passwords", 403)

         # Ensure password are the same
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 403)


        #from app import User
        me = User(username=str(request.form.get("username")), password=str(generate_password_hash(request.form.get("password"))), API_KEY1=request.form.get("api"), API_KEY2=request.form.get("api2"))
        db.session.add(me)
        db.session.commit()

        # Remember which user has logged in
        tmp = User.query.filter_by(username=x).first()

        session["user_id"] = tmp.id

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
#class asdf(Thread):
#    def run():
#        print("asdf")
on = False

if __name__ == '__main__':
    app.run(threaded=True)
    v = asdf(on)
    t = threading.Thread(target=algo(), args=(1,), daemon=True)
    t.run_forever()
