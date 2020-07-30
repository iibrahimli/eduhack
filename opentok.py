import time
import os
from configparser import ConfigParser
from opentok import OpenTok, MediaModes, ArchiveModes, Roles


# ============= init =============

# parse config
config = ConfigParser()
config.read('config.ini')
opentok_api_key = config.get('tokens', 'opentok_api_key')
opentok_api_secret = config.get('tokens', 'opentok_api_secret')

# init opentok
opentok = OpenTok(opentok_api_key, opentok_api_secret)


# ============= opentok setup =============

# automatically archived session
session = opentok.create_session(media_mode=MediaModes.routed)
session_id = session.session_id

token = session.generate_token()

# Set some options in a token
token = session.generate_token(role=Roles.moderator,
                               expire_time=int(time.time()) + 10,
                               data=u'name=Johnny'
                               initial_layout_class_list=[u'focus'])