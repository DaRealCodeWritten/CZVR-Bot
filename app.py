import os
import requests
from urllib import parse
from flask import Flask, render_template, request, redirect


app = Flask(__name__)


@app.route('/', methods=["GET", "POST"])
def hello_world():  # put application's code here
    if request.method == "GET":
        return render_template("home.html")
    elif request.method == "POST":
        return redirect("https://discord.com/api/oauth2/authorize?client_id=947062830358736897&redirect_uri=https%3A%2F%2Fczvr-bot.herokuapp.com%2Fdiscord%2Foauth%2F&response_type=code&scope=identify%20guilds.join")


@app.route('/discord/oauth/', methods=["GET",])
def authorized_discord():
    data = {
        "code": request.args.get("code"),
        "client_id": os.environ.get("CLIENT_ID"),
        "client_secret": os.environ.get("CLIENT_SECRET"),
        "grant_type": "authorization_code",
        "redirect_uri": "czvr-bot.herokuapp.com/discord/success/"
    }
    header = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    r = requests.post("https://discord.com/api/v8/oauth2/token", headers=header, data=data)
    print(r.json())
    return redirect("https://czvr-bot.herokuapp.com/discord/success")


@app.route("/discord/success")
def discord_success():
    return render_template("discord_success.html")


try:
    with open("key.pem", "w") as key:
        key.write(os.environ.get("SSL_KEY"))
    with open("cert.pem", "w") as cert:
        cert.write(os.environ.get("SSL_CERT"))
    app.run(None, 80, ssl_context=("cert.pem", "key.pem"))
except Exception as e:
    print(e)
