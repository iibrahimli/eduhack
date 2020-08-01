import time
import os
from configparser import ConfigParser
from opentok import OpenTok, MediaModes, Roles


class OpenTokServer:
    """ OpenTok wrapper. For now only supports a single session """

    def __init__(self):
        config = ConfigParser()
        config.read('config.ini')
        opentok_api_key = config.get('tokens', 'opentok_api_key')
        opentok_api_secret = config.get('tokens', 'opentok_api_secret')
        self.opentok = OpenTok(opentok_api_key, opentok_api_secret)
        self.session = None
    

    def create_session(self):
        """
        Create an OpenTok session, get session ID and (moderator) token

        Returns:
            str, Session ID or None on error
        """

        self.session = self.opentok.create_session(
            media_mode=MediaModes.routed
        )
        return self.session.session_id


    def get_session_id(self):
        """
        Query session ID if session is active

        Returns:    
            str, Session ID or None if no session is active
        """

        return self.session.session_id


    def generate_token(self, username):
        """
        Generate a token for session if active (username stored in metadata)

        Returns:
            str, Token or None if no active session
        """

        if self.session is not None:
            return self.session.generate_token(
                role=Roles.publisher,
                data=f"username={username}"
            )
        else:
            return None