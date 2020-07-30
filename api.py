import os
import time
import json
from flask import Flask, request, abort, jsonify
from configparser import ConfigParser

from database import Database


def parse_default_accounts(config):
    usernames = config.get('users', 'usernames').split(',')
    passwords = config.get('users', 'passwords').split(',')
    status = config.get('users', 'is_examiner').split(',')
    return [
        (uname, upass, is_exm) for uname, upass, is_exm in zip(
            map(str.strip, usernames),
            map(str.strip, passwords),
            map(str.strip, status)
        )
    ]


# ============= init =============

# parse config
config = ConfigParser()
config.read('config.ini')
db_path = config.get('db', 'path')

# init database
db = Database(db_path)

# create default users if don't exist
default_accounts = parse_default_accounts(config)
for acc in default_accounts:
    db.create_user(*acc)

# init flask app
app = Flask(__name__)


# ============= flask routes =============

@app.route('/api/auth', methods=["POST"])
def auth():
    """
    Authenticate a user.

    Request (JSON):
    {
        "username": "user1",
        "password": "pass1"
    }

    Response (JSON):
    {
        "correct": true,
        "is_examiner": false
    }
    """

    if not request or request.method != "POST":
        return abort(405)

    username = request.json.get("username")
    password = request.json.get("password")

    if username is None or password is None:
        return abort(406)
    
    user_data = db.get_user_data(username)
    
    if user_data is not None and password == user_data["password"]:
        return jsonify({
            "correct": True,
            "is_examiner": user_data["is_examiner"]
        })
    else:
        return jsonify({
            "correct": False,
            "is_examiner": False
        })