from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route("/")
@app.route("/login")
def login():
    app.logger.debug("login request")
    return render_template("login.html", name="Yiming")


@app.route("/register")
def register():
    app.logger.debug("register request")
    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    app.logger.debug("dashboard request")
    return render_template("dashboard.html")