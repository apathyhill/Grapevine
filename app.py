import os
import flask
from flask import Flask, request, redirect, make_response, render_template
from db_model import db
from api import API
from decouple import config

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = config("DATABASE_URI")

### HELPER FUNCTIONS ###

# Set cookies
def cookie_set(destination, key, value):
    resp = make_response(destination)
    resp.set_cookie(key, value)
    return resp

### GENERAL PAGES ###

# Home page
@app.route("/")
def home():
    user = api.user_current(request)
    if not user:
        return redirect("/login")
    return render_template("home.html")

# Create post
# TODO: Go to post
@app.route("/post/submit", methods=["POST"])
def post_handler():
    response = api.post_create(request)
    return response.get("message", "")

# User profile
@app.route("/user/<username>")
@app.route("/user_id/<id>")
def user_profile(**kwargs):
    response = api.user_profile(request, **kwargs)
    if response["code"] == 200:
        return render_template("user_profile.html", data=response["data"])
    return response["message"]

### USER LOGIN ###

# Login Page
@app.route("/login")
def login():
    user = api.user_current(request)
    if user:
        return redirect("/")
    return render_template("login.html")

# Login handler
@app.route("/login/submit", methods=["POST"])
def login_handler():
    response = api.user_login(request)
    if response["code"] == 200:
        return cookie_set(redirect("/"), "session_key", response["session_key"])
    return redirect("/login")

### USER REGISTER ###

# Registration page
@app.route("/register")
def register():
    user = api.user_current(request)
    if user:
        return redirect("/")
    return render_template("register.html")

# Registration handler
@app.route("/register/submit", methods=["POST"])
def register_handler():
    response = api.user_register(request)
    if response["code"] == 201:
        return cookie_set(redirect("/"), "session_key", response["session_key"])
    return redirect("/login")

if __name__ == "__main__":
    db.app = app
    db.init_app(app)
    db.create_all()
    api = API(db)
    app.run()