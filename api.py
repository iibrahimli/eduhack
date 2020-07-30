import time
import os
from configparser import ConfigParser
from flask import Flask


# ============= init =============

# parse config
config = ConfigParser()
config.read('config.ini')

# init flask app
app = Flask(__name__)


# ============= flask routes =============

@app.route('/')
def hello():
    return "test response"