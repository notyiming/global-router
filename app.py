from flask import Flask, session, render_template, request, redirect
import pyrebase

app = Flask(__name__)

config = {
    "apiKey": "AIzaSyBLWI2VvmKXXUeFeQlqjDB-0Gcpd1Oj_AQ",
    "authDomain": "global-router.firebaseapp.com",
    "projectId": "global-router",
    "storageBucket": "global-router.appspot.com",
    "messagingSenderId": "692743036864",
    "appId": "1:692743036864:web:e5738b41fe4afe26123225",
    "measurementId": "G-YG6SFLCQ0X",
    "databaseURL": ""
}

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
    app.logger.debug("dashboard request")
    return render_template("dashboard.html")