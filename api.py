import os
import json
import datetime
import pytz
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from configparser import ConfigParser


from database import Database
from opentokserver import OpenTokServer


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

def log(*args):
    global VERBOSE
    if VERBOSE is True:
        BAKU_TIMEZONE = pytz.timezone("Asia/Baku")
        dt = datetime.datetime.now().astimezone(BAKU_TIMEZONE)
        dt_str = dt.strftime("%Y/%m/%d %H:%M:%S")
        print(f"[DEBUG] [{dt_str}] ", *args)


def auth_user(db, username, password):
    """
    Authenticate a user
    """

    user_data = db.get_user_data(username)

    return (user_data is not None and \
            password == user_data["password"] and \
            user_data["in_session"] is None)


# ============= init =============

# parse config
config = ConfigParser()
config.read('config.ini')
db_path = config.get('db', 'path')
VERBOSE = config.getboolean('general', 'debug')

# init database
db = Database(db_path)
db.clear_sessions()
log("Initialized database")

# create default users if don't exist
default_accounts = parse_default_accounts(config)
for acc in default_accounts:
    db.create_user(*acc)

# init opentok server
tokserver = OpenTokServer()
log("Initialized OpenTokServer")

# init flask app
app = Flask(__name__)
cors = CORS(app)

log("Initialized API")


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

    log(f"Auth requested for {username}:{password}")

    if auth_user(db, username, password):
        return jsonify({
            "success": True,
            "user_id": user_data["user_id"],
            "display_name": user_data["display_name"],
            "initials": user_data["initials"],
            "is_examiner": user_data["is_examiner"]
        })
    else:
        return jsonify({
            "success": False
        })


@app.route('/api/logout', methods=["POST"])
def logout():
    """
    Log a user out.

    Request (JSON):
    {
        "username": "user1",
        "password": "pass1"
    }

    Response (JSON):
    {
        "success": true
    }
    """

    if not request or request.method != "POST":
        return abort(405)

    username = request.json.get("username")
    password = request.json.get("password")

    if username is None or password is None:
        return abort(406)
    
    user_data = db.get_user_data(username)

    log(f"Logout requested for {username}:{password}")

    return jsonify({
        "success": (auth_user(db, username, password) and \
                    db.logout_user(username))
    })


@app.route('/api/session/create', methods=["POST"])
def create_session():
    """
    Create a session.

    Request (JSON):
    {
        "username": "examiner",
        "password": "pass",
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
    password = request.json.get("password")
    session_password = request.json.get("session_password")

    if username is None or session_password is None or password is None:
        return abort(406)
    
    session_id = tokserver.create_session()
    session_token = tokserver.generate_token(username)

    if auth_user(db, username, password) and \
       db.add_session(username, session_id, session_password) is not None and \
       db.add_user_to_session(username, session_id, session_token):
        log(f"Created session {session_id} (creator: {username})")
        return jsonify({
            "success": True,
            "session_id": session_id,
            "session_token": session_token
        })
    else:
        return jsonify({
            "success": False,
        })


@app.route('/api/session/join', methods=["POST"])
def join_session():
    """
    Join a session.

    Request (JSON):
    {
        "username": "studt",
        "password": "datte",
        "session_id": "1234",
        "session_password": "pass"
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
    password = request.json.get("password")
    session_id = request.json.get("session_id")
    session_password = request.json.get("session_password")

    if username is None or password is None \
       or session_id is None or session_password is None:
        return abort(406)

    session_data = db.get_session_data(session_id)
    session_token = tokserver.generate_token(username)

    if session_data is not None and \
       auth_user(db, username, password) and \
       session_data["password"] == session_password and \
       db.add_user_to_session(username, session_id, session_token):
        log(f"Added user {username} to session {session_id}")
        return jsonify({
            "success": True,
            "session_id": session_id,
            "session_token": session_token
        })
    else:
        return jsonify({
            "success": False,
        })


@app.route('/api/session/users', methods=["POST"])
def session_users():
    """
    Get list of users in the session

    Request (JSON):
    {
        "session_id": "1234",
        "session_password": "pass"
    }

    Response (JSON):
    {
        "success": true,
        "users": [
            {
                "user_id": 2,
                "display_name": "Us A",
                "is_examiner": true
            },
            {
                "user_id": 1,
                "display_name": "Us B",
                "is_examiner": false
            }
        ]
    }
    """

    if not request or request.method != "POST":
        return abort(405)

    session_id = request.json.get("session_id")
    session_password = request.json.get("session_password")

    if session_id is None or session_password is None:
        return abort(406)

    session_data = db.get_session_data(session_id)

    if session_data is not None and \
       session_data["password"] == session_password:
        return jsonify({
            "success": True,
            "users": session_data["users"]
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

# from OpenSSL import SSL
# context = ('/home/stud/certs/studium.me/cert1.pem', '/home/stud/certs/studium.me/privkey1.pem')
# context = SSL.Context(SSL.PROTOCOL_TLSv1_2)
# context.use_privatekey_file('/home/stud/certs/studium.me/privkey1.pem')
# context.use_certificate_file('/home/stud/certs/studium.me/cert1.pem')
# 
# app.run(debug=True, ssl_context=context)
