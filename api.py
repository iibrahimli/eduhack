import os
import time
import json
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from configparser import ConfigParser


from database import Database
# from tokserver import OpenTokServer


def parse_default_accounts(config):
    usernames = config.get('users', 'usernames').split(',')
    disp_names = config.get('users', 'disp_names').split(',')
    passwords = config.get('users', 'passwords').split(',')
    status = config.get('users', 'is_examiner').split(',')
    return [
        (uname, disp_name, upass, is_exm) for uname, disp_name, upass, is_exm in zip(
            map(str.strip, usernames),
            map(str.strip, disp_names),
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

# init opentok server
# TODO

# init flask app
app = Flask(__name__)
cors = CORS(app)


# ============= endpoints =============

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
        "success": true,
        "user_id": 3,
        "display_name": "Kamal Agayev",
        "initials": "KA",
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

    if user_data is not None and \
       password == user_data["password"] and \
       user_data["in_session"] is None:
        return jsonify({
            "success": True,
            "user_id": user_data["id"],
            "display_name": user_data["display_name"],
            "initials": user_data["initials"],
            "is_examiner": user_data["is_examiner"]
        })
    else:
        return jsonify({
            "success": False
        })


@app.route('/api/session/create', methods=["POST"])
def create_session():
    """
    Create a session.

    Request (JSON):
    {
        "username": "examiner",
        "session_password": "p@ssw0rd"
    }

    Response (JSON):
    {
        "success": true,
        "session_id": 165432114,
        "session_token": "cas5c45as4d"
    }
    """

    if not request or request.method != "POST":
        return abort(405)

    username = request.json.get("username")
    session_password = request.json.get("session_password")

    if username is None or session_password is None:
        return abort(406)
    
    user_data = db.get_user_data(username)

    if user_data is not None and \
       user_data["is_examiner"] is True:
        return jsonify({
            "success": True,
            "user_id": user_data["id"],
            "display_name": user_data["display_name"],
            "initials": user_data["initials"],
            "is_examiner": user_data["is_examiner"]
        })
    else:
        return jsonify({
            "success": False,
        })


@app.route('/api/monitor', methods=["POST"])
def monitor():
    """
    OpenTok stream events monitoring
    https://tokbox.com/developer/guides/session-monitoring/
    """

    if not request or request.method != "POST":
        return abort(405)

    return jsonify({'success':True}), 200, {'ContentType':'application/json'}