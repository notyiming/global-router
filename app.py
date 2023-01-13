from flask import Flask, flash, session, render_template, request, redirect
from requests import HTTPError
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
            if auth.get_account_info(user["idToken"])["users"][0]["emailVerified"]:
                session["user"] = email
                return redirect("/dashboard")
            else:  # email not verified
                flash("Email has not been verified yet", "error")
                return redirect("/login")
        except:
            flash("Invalid Credentials", "error")
            return redirect("/login")
    return render_template("login.html")


@app.route("/resetPassword", methods=["POST", "GET"])
def reset_password():
    if request.method == "POST":
        email = request.form.get("email_to_reset")
        auth.send_password_reset_email(email)

        # notify user that password reset link has been sent
        flash(f"Password reset link sent to {email}", "info")
        return redirect("/login")
    elif request.method == "GET":
        return render_template("reset_password.html")


@app.route("/logout")
def logout():
    session.pop("user")
    flash("Logged out successfully", "info")
    return redirect("/login")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        try:
            user = auth.create_user_with_email_and_password(email, password)
            auth.send_email_verification(user["idToken"])
            flash("Account created, please verify email", "info")
            return redirect("/login")
        except HTTPError as e:
            e = str(e)
            if "EMAIL_EXISTS" in e:
                flash("Email already taken", "error")
            elif "WEAK_PASSWORD" in e:
                flash("Password should be at least 6 characters", "error")
            else:
                flash("Other HTTP error occured", "error")
            return redirect("/register")

    elif request.method == "GET":
        return render_template("register.html")


@app.route("/dashboard")
def dashboard():
    if not "user" in session:
        return redirect("/login")
    app.logger.debug("dashboard request")
    return render_template("dashboard.html", user=session["user"])
