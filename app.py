from flask import Flask, session, render_template, request, redirect
from fbconfig import config
import pyrebase

app = Flask(__name__)

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

app.secret_key = "ming"

@app.route("/")
@app.route("/login", methods=["POST", "GET"])
def login():
    if "user" in session:
        return redirect("/dashboard")
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session["user"] = email
            return redirect("/dashboard")
        except:
            return "Failed to Login"
    return render_template("login.html")

@app.route("/resetPassword", methods=["POST", "GET"])
def reset_password():
    if request.method == "POST":
        email = request.form.get("email_to_reset")
        auth.send_password_reset_email(email)
        # notify user that password reset link has been sent
        return redirect("/login")
    elif request.method == "GET":
        return render_template("reset_password.html")


@app.route("/logout")
def logout():
    session.pop("user")
    return redirect("/login")


@app.route("/register")
def register():
    app.logger.debug("register request")
    return render_template("register.html")


@app.route("/dashboard")
def dashboard():
    if not "user" in session:
        return redirect("/login")
    app.logger.debug("dashboard request")
    return render_template("dashboard.html")
