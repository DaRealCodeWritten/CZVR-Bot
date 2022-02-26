import os
import requests
from flask import Flask, render_template, request, redirect


app = Flask(__name__)


@app.route('/', methods=["GET", "POST"])
def hello_world():  # put application's code here
    if request.method == "GET":
        return render_template("home.html")
    elif request.method == "POST":
        return redirect("https://discord.com/api/oauth2/authorize?client_id=947062830358736897&redirect_uri=https%3A%2F%2Fczvr-role-bot.herokuapp.com%2Fdiscord%2Foauth%2F&response_type=code&scope=identify%20guilds.join")


@app.route('/discord/oauth/?code=<code>&state=<state>')
def authorized_discord():
    code = request.args.get("code")
    data = {
        "code": code,
        "client_id": os.environ.get("CLIENT_ID"),
        "client_secret": os.environ.get("CLIENT_SECRET"),
        "grant_type": "authorization_code",
        "redirect_uri": "https://czvr-role-bot.herokuapp.com/discord/success"
    }
    header = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    r = requests.post("https://discord.com/api/v8/oauth2/token", headers=header, data=data)
    print(r.json())


@app.route("/discord/success")
def discord_success():
    return render_template("discord_success.html")


try:
    app.run(None, 80, ssl_certificate="adhoc")
except:
    pass
