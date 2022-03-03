import os
import auth
import psycopg2
import requests
from flask import Flask, render_template, request, redirect


config = auth.return_auth()
app = Flask(__name__)
db = psycopg2.connect(
    database=config["DATABASE"],
    user=config["USER"],
    host=config["HOST"],
    password=config["PASS_DEV"],
    port="5432"
)


@app.route('/', methods=["GET", "POST"])
def hello_world():  # put application's code here
    """Index route func, move along"""
    if request.method == "GET":
        return render_template("home.html")
    elif request.method == "POST":
        return redirect("https://discord.com/api/oauth2/authorize?client_id=947062830358736897&redirect_uri=https%3A%2F%2Fczvr-bot.xyz%2Fdiscord%2Foauth%2F&response_type=code&scope=identify%20guilds.join")


@app.route('/discord/oauth/', methods=["GET",])
def authorized_discord():
    """Callback URI from Discord OAuth"""
    data = {
        "code": request.args.get("code"),
        "client_id": config["CLIENT_ID"],
        "client_secret": config["CLIENT_SECRET"],
        "grant_type": "authorization_code",
    }
    header = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    r = requests.post("https://discord.com/api/v8/oauth2/token", headers=header, data=data)
    print(r.json())
    return redirect("https://czvr-bot.xyz/discord/success")


@app.route("/discord/success")
def discord_success():
    """Route func for successful integration with Discord"""
    return render_template("discord_success.html")


try:
    app.run(None, 80)
except Exception as e:
    print(e)
