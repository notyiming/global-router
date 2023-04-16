"""Flask App"""

import base64
from datetime import datetime
import glob
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
db = firebase.database()
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
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        try:
            user = auth.create_user_with_email_and_password(email, password)
            auth.send_email_verification(user["idToken"])
            encoded_email = base64.urlsafe_b64encode(
                email.encode()).decode().rstrip("=")
            db.child("users").child(encoded_email).set(
                {"fname": fname, "lname": lname, "email": email})
            flash("Account created, please verify email", "info")
            return redirect("/login")
        except HTTPError as error:
            error = str(error)
            if "EMAIL_EXISTS" in error:
                flash("Email already taken", "error")
            elif "WEAK_PASSWORD" in error:
                flash("Password should be at least 6 characters", "error")
            else:
                flash(error, "error")
            return redirect("/register")

    elif request.method == "GET":
        return render_template("register.html")


@app.route("/download/<path:filename>")
def download(filename):
    """Download Output File"""
    if "user" not in session:
        return redirect("/login")
    encoded_email = base64.urlsafe_b64encode(
        session["user"].encode()).decode().rstrip("=")
    user = db.child("users").child(encoded_email).get().val()
    return redirect(storage.child(f"{user['email']}/{filename}").get_url(None))


@app.route("/dashboard", methods=["POST", "GET"])
def dashboard():
    """Launch User Dashboard"""
    encoded_email = base64.urlsafe_b64encode(
        session["user"].encode()).decode().rstrip("=")
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        input_file = request.files.get("input-file", None)
        algorithm = int(request.form.get("algorithm-select"))
        seed = int(request.form.get("seed-input"))
        if input_file:
            filename = secure_filename(input_file.filename)
            netlist_file = os.path.join(
                app.config["UPLOAD_FOLDER"], filename)
            input_file.save(netlist_file)
            file_basename = Path(netlist_file).stem

        else:
            netlist_file = request.form.get("sample-netlist-select")
            file_basename = Path(netlist_file).stem

        # if output directory does not exist, create it
        os.makedirs("output", exist_ok=True)

        netlist_details, overflow, wirelength = gr.global_route.callback(
            netlist_file, f"output/{file_basename}.out", algorithm, seed)

        timenow = datetime.now()
        formatted_timenow = timenow.strftime('%Y-%m-%d %H:%M:%S')
        unix_timenow = int(timenow.timestamp())

        result = {
            "netlist_details": netlist_details,
            "name": file_basename,
            "overflow": overflow,
            "wirelength": wirelength,
            "timestamp": formatted_timenow,
            "unique_name": f"{file_basename}_{unix_timenow}",
            "fig_html": gr.plot_congestion.callback(f"output/{file_basename}.out.fig"),
            "algorithm": [
                "Best First Search (Binary Heap)",
                "Best First Search (Fibonacci Heap)",
                "Breadth First Search"
            ][algorithm - 1]
        }

        db.child("users").child(encoded_email).child("outputs").push(result)
        storage.child(
            f"{session['user']}/{result['unique_name']}").put(f"output/{file_basename}.out")

        # remove output file after saving to firebase
        for output_file in glob.glob(f"output/{file_basename}*"):
            os.remove(output_file)

        return jsonify(result)

    user = db.child("users").child(encoded_email).child("fname").get().val()
    outputs = db.child("users").child(
        encoded_email).child("outputs").get().val()
    return render_template("dashboard.html", user=user, outputs=outputs.values() if outputs else [])


if __name__ == '__main__':
    app.run(debug=True)
