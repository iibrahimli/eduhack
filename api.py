import os
import time
import json
from flask import Flask
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


# init flask app
app = Flask(__name__)

# init database
db = Database(db_path)

# create default users if don't exist
default_accounts = parse_default_accounts(config)
for acc in default_accounts:
    db.create_user(*acc)

# ============= flask routes =============

@app.route('/')
def hello():
    return "test response"