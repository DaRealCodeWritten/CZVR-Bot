import auth
from urllib import parse
import psycopg2
import requests
from flask_login import LoginManager, login_user, current_user, logout_user, UserMixin, login_required
from flask import Flask, render_template, request, redirect, abort, send_from_directory


config = auth.return_auth()
users = {}
app = Flask(__name__)
app.secret_key = config["SITE_CLIENT_SECRET"]
log_man = LoginManager()
log_man.init_app(app)


class User(UserMixin):
    def __init__(self, cid: int):
        self.alternative_id = str(cid)

    def get_id(self):
        return self.alternative_id

    @property
    def is_authenticated(self):
        return (users.get(self.alternative_id) is not None)


@log_man.user_loader
def load_user(user_id: str):
    return users.get(user_id)


db = psycopg2.connect(
    database=config["DATABASE"],
    user=config["USER"],
    host=config["HOST"],
    password=config["PASS_DEV"],
    port="5432"
)


@app.route('/', methods=["GET", "POST"])
def hello_world():
    """Index route func, move along"""
    return render_template("home.html")


@app.route("/vatsim")
def sso():
    return render_template("login.html")


@login_required
@app.route('/discord/oauth/', methods=["GET",])
def authorized_discord():
    """Callback URI from Discord OAuth"""
    data = {
        "code": request.args.get("code"),
        "client_id": config["CLIENT_ID"],
        "client_secret": config["CLIENT_SECRET"],
        "grant_type": "authorization_code",
        "redirect_uri": "https%3A%2F%2Fserver.czvr-bot.xyz%3A5000/discord/success"
    }
    header = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    r = requests.post("https://discord.com/api/oauth2/token", headers=header, data=data)
    data = r.json()
    token = data.get("access_token")
    if token is None:
        return data
    header["Authorization"] = f"Bearer {token}"
    udata = requests.get("https://discord.com/api/users/@me", headers=header)
    uid = udata.json().get("id")
    if uid is None:
        return abort(403)
    crs = db.cursor()
    crs.execute(f"UPDATE {config['DATABASE_TABLE']} SET dcid = ? WHERE cid = ?", (uid, int(current_user.get_id())))
    crs.close()
    db.commit()
    header.pop("Content-Type")
    header["Authorization"] = config["TOKEN"]
    data = {
        "access_token": f"Bearer {token}"
    }
    requests.put(f"https://discord.com/api/guilds/947764065118335016/members/{uid}", data=data, headers=header)
    return redirect("https://czvr-bot.xyz/discord/success")


@app.route("/discord/success")
def discord_success():
    """Route func for successful integration with Discord"""
    return render_template("discord_success.html")


@app.route("/vatsim/oauth")
def vatsim_link():
    """Redirect URL to link to VATSIM"""
    try:
        data = {
            "client_id": config["VATSIM_CLIENT_ID"],
            "client_secret": config["VATSIM_CLIENT_SECRET"],
            "code": request.args.get("code"),
            "grant_type": "authorization_code",
            "redirect_uri": "https://server.czvr-bot.xyz:5000/vatsim/oauth"
        }
        returned = requests.post(f"{config['VATSIM_AUTH']}/oauth/token", data=data)
        jsonify = returned.json()
        token = jsonify.get("access_token")
        if token is None: # Site probably threw an error, FAIL
            return "Failed, no token"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
        user_data = requests.get(f"{config['VATSIM_AUTH']}/api/user", headers=headers)
        juser = user_data.json()
        udata = juser.get("data")
        if udata is None: # Site threw an error AGAIN FAIL
            return f"Failed, no user data"
        cid = int(udata.get("cid"))
        crs = db.cursor()
        try:
            crs.execute(f"INSERT INTO {config['DATABASE_TABLE']} VALUES (? ? ?)", (cid, 0, 0))
        except:
            pass
        crs.close()
        db.commit()
        user = User(cid)
        login_user(user)
        users[str(cid)] = user
        return redirect("https://server.czvr-bot.xyz:5000/profile")
    except Exception as e:
        print(e)
        return e.__str__()


@login_required
@app.route("/profile")
def profile():
    return render_template("profile.html", cid=current_user.get_id())


@login_required
@app.route("/logout")
def logout():
    users.pop(current_user.get_id())
    logout_user()
    return render_template("logout.html")


if __name__ == "__main__":
    try:
        app.run("0.0.0.0", 80)
    except Exception as e:
        print(e)
