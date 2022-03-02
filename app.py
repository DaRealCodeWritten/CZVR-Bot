import os
import psycopg2
import requests
import subprocess
from flask import Flask, render_template, request, redirect


app = Flask(__name__)
db = psycopg2.connect(
    database="dekd8sq403uspf",
    user="tpgzyglxzdlzgq",
    host="ec2-34-231-183-74.compute-1.amazonaws.com",
    password=os.environ.get("DB_PASS"),
    port="5432"
)
dbcrs = db.cursor()

@app.route('/', methods=["GET", "POST"])
def hello_world():  # put application's code here
    """Index route func, move along"""
    if request.method == "GET":
        return render_template("home.html")
    elif request.method == "POST":
        return redirect("https://discord.com/api/oauth2/authorize?client_id=947062830358736897&redirect_uri=https%3A%2F%2Fczvr-bot.herokuapp.com%2Fdiscord%2Foauth%2F&response_type=code&scope=identify%20guilds.join")


@app.route('/discord/oauth/', methods=["GET",])
def authorized_discord():
    """Callback URI from Discord OAuth"""
    data = {
        "code": request.args.get("code"),
        "client_id": os.environ.get("CLIENT_ID"),
        "client_secret": os.environ.get("CLIENT_SECRET"),
        "grant_type": "authorization_code",
    }
    header = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    r = requests.post("https://discord.com/api/v8/oauth2/token", headers=header, data=data)
    print(r.json())
    return redirect("https://czvr-bot.herokuapp.com/discord/success")


@app.route("/discord/success")
def discord_success():
    """Route func for successful integration with Discord"""
    return render_template("discord_success.html")


try:
    with open("key.pem", "w") as key:
        key.write(os.environ.get("SSL_KEY"))
    with open("cert.pem", "w") as cert:
        cert.write(os.environ.get("SSL_CERT"))
    subprocess.run("python bot.py")
    app.run(None, 80, ssl_context=("cert.pem", "key.pem"))
except Exception as e:
    print(e)
