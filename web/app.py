"""Flask App"""

from pathlib import Path
import os
from flask import Flask, flash, jsonify, session, render_template, request, redirect
from werkzeug.utils import secure_filename
from requests import HTTPError
import pyrebase
from dotenv import dotenv_values
import gr


UPLOAD_FOLDER = 'uploaded_netlists'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


config = dotenv_values()

# for readthedocs, since .env is secret
if len(config) == 0:
    config = {
        "apiKey": "",
        "authDomain": "",
        "projectId": "",
        "storageBucket": "",
        "messagingSenderId": "",
        "appId": "",
        "measurementId": "",
        "databaseURL": "",
        "secretKey": ""
    }

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
storage = firebase.storage()
app.secret_key = config["secretKey"]


@app.route("/")
@app.route("/login", methods=["POST", "GET"])
def login():
    """Login"""
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
            flash("Email has not been verified yet", "error")
            return redirect("/login")
        except HTTPError:
            flash("Invalid Credentials", "error")
            return redirect("/login")
    return render_template("login.html")


@app.route("/resetPassword", methods=["POST", "GET"])
def reset_password():
    """Password Reset"""
    if request.method == "POST":
        email = request.form.get("email_to_reset")
        auth.send_password_reset_email(email)

        # notify user that password reset link has been sent
        flash(f"Password reset link sent to {email}", "info")
        return redirect("/login")
    if request.method == "GET":
        return render_template("reset_password.html")


@app.route("/logout")
def logout():
    """Log Out"""
    session.pop("user")
    flash("Logged out successfully", "info")
    return redirect("/login")


@app.route("/register", methods=["POST", "GET"])
def register():
    """Register for a new Account"""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        try:
            user = auth.create_user_with_email_and_password(email, password)
            auth.send_email_verification(user["idToken"])
            flash("Account created, please verify email", "info")
            return redirect("/login")
        except HTTPError as error:
            error = str(error)
            if "EMAIL_EXISTS" in error:
                flash("Email already taken", "error")
            elif "WEAK_PASSWORD" in error:
                flash("Password should be at least 6 characters", "error")
            else:
                flash("Other HTTP error occured", "error")
            return redirect("/register")

    elif request.method == "GET":
        return render_template("register.html")


@app.route("/dashboard", methods=["POST", "GET"])
def dashboard():
    """Lauch User Dashboard"""
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        if not request.files:
            netlist_file = (request.get_data().decode())
            file_basename = Path(netlist_file).stem

        else:
            if "inputFile" not in request.files:
                flash("No file part", "error")
                return redirect("/dashboard")
            file = request.files["inputFile"]
            if not file.filename:
                flash("No selected file", "error")
                return redirect("/dashboard")
            if file and _allowed_file(file.filename):
                filename = secure_filename(file.filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                netlist_file = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(netlist_file)

        result = {}
        file_basename = Path(netlist_file).stem
        result["img_src"] = f"static/{file_basename}.png"
        result["netlist_details"] = gr.global_route.callback(netlist_file, f"output/{file_basename}.out")
        gr.plot_congestion.callback(f"output/{file_basename}.out.fig", f"web/static/{file_basename}.png")

        return jsonify(result)


    return render_template("dashboard.html", user=session["user"])

def _allowed_file(filename: str) -> bool:
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() == "txt"


if __name__ == '__main__':
    app.run(debug=True)
