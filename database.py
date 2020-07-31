import sqlite3
from sqlite3 import Error


_queries = {
    'create_users_table': """
        CREATE TABLE IF NOT EXISTS users (
            id integer PRIMARY KEY AUTOINCREMENT,
            username text NOT NULL,
            display_name text NOT NULL,
            initials text NOT NULL,
            password text NOT NULL,
            is_examiner integer DEFAULT 0 NOT NULL,
            in_session text DEFAULT NULL,
            session_token text DEFAULT NULL
        );
        """,

    'create_sessions_table': """
        CREATE TABLE IF NOT EXISTS sessions (
            id text PRIMARY KEY,
            password text NOT NULL,
            creator_id integer NOT NULL
        );
        """,

    'create_user': """
        INSERT INTO users
            (username, display_name, initials, password, is_examiner)
            VALUES
            (?, ?, ?, ?, ?)
        """,
    
    'create_session': """
        INSERT INTO sessions
            (id, password, creator_id)
            VALUES
            (?, ?, ?)
        """
}


class Database:
    """ Simple database class """

    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = self.create_conn()
        self.create_tables()


    def create_conn(self):
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            return conn
        except Error as e:
            print(e)

        return conn
    

    def create_tables(self):
        try:
            cur = self.conn.cursor()
            cur.execute(_queries['create_users_table'])
            cur.execute(_queries['create_sessions_table'])
            self.conn.commit()
        except Error as e:
            print(e)
    

    def create_user(self, username, display_name, password, is_examiner=False):
        """
        Create a user if does not exist
        
        Args:
            username (str): Username
            password (str): Password
            display_name (str): Display name
            is_examiner (bool): Is examiner?
        """

        cur = self.conn.cursor()
        if self.get_user_data(username) is None:
            is_examiner = int(is_examiner)
            initials = display_name.split(' ')[0][0].upper() + \
                       display_name.split(' ')[1][0].upper()
            cur.execute(
                _queries['create_user'],
                (username, display_name, initials, password, is_examiner)
            )
            self.conn.commit()


    def get_user_data(self, username):
        """
        Query user data by username

        Args:
            username (str): Username
        
        Returns:
            dict, User data
        """

        cur = self.conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        rows = cur.fetchall()
        if not rows:
            return None
        return {
            "id": rows[0][0],
            "username": rows[0][1],
            "display_name": rows[0][2],
            "initials": rows[0][3],
            "password": rows[0][4],
            "is_examiner": bool(rows[0][5]),
            "in_session": rows[0][6],
            "session_token": rows[0][7]
        }


    def create_session(self, username, session_id, session_password):
        """
        Create a session if does not exist
        
        Args:
            username (str): Username
            session_id (str): Session ID
            session_password (str): Session password
        
        Returns:
            dict, Session data or None on error
        """

        cur = self.conn.cursor()
        user_data = self.get_user_data(username)
        creator_id = user_data["id"]
        if user_data is not None and \
           user_data["is_examiner"] is True and \
           user_data["in_session"] is None:
            cur.execute(
                _queries['create_session'],
                (session_id, session_password, creator_id)
            )
            self.conn.commit()
            return {
                "id": session_id,
                "password": session_password,
                "creator_id": creator_id
            }
        else:
            return None


    def get_session_data(self, session_id):
        """
        Query session data by session_id

        Args:
            session_id (str): Session ID
        
        Returns:
            dict, Session data
        """

        cur = self.conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        rows = cur.fetchall()
        if not rows:
            return None
        return {
            "id": rows[0][0],
            "username": rows[0][1],
            "password": rows[0][2],
            "is_examiner": bool(rows[0][3]),
            "in_session": rows[0][4]
        }