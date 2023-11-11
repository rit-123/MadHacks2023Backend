import os

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import *
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime



# Configure application
app = Flask(__name__)



@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/login", methods=["GET","POST"])
def login():

    return "rese", 600
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # confirmpassword = request.form.get("confirmpassword")

        # Make sure username is not empty
        if not username:
            return json.dumps({"err":"ranodm err"}), 400
        # Make sure username doesn't already exist

        # Make sure passwords and confirm password match

        # add user and hashed password to the database

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, dubug=True)