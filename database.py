import sqlite3
from sqlite3 import Error


_queries = {
    'create_users_table': """
        CREATE TABLE IF NOT EXISTS users (
            user_id integer PRIMARY KEY AUTOINCREMENT,
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
            session_id text PRIMARY KEY,
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
            (session_id, password, creator_id)
            VALUES
            (?, ?, ?)
        """,
    
    'add_user_to_session': """
        UPDATE users
            SET in_session = ? ,
                session_token = ?
            WHERE username = ?
        """,
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
    

    def clear_sessions(self):
        try:
            cur = self.conn.cursor()
            cur.execute("DELETE FROM sessions;")
            cur.execute("""
                UPDATE users
                SET in_session = null ,
                    session_token = null;
            """)
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
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        rows = cur.fetchall()
        if not rows:
            return None
        return {
            "user_id": rows[0][0],
            "username": rows[0][1],
            "display_name": rows[0][2],
            "initials": rows[0][3],
            "password": rows[0][4],
            "is_examiner": bool(rows[0][5]),
            "in_session": rows[0][6],
            "session_token": rows[0][7]
        }


    def add_session(self, username, session_id, session_password):
        """
        Add a session if does not exist
        
        Args:
            username (str): Username
            session_id (str): Session ID
            session_password (str): Session password
        
        Returns:
            dict, Session data or None on error
        """

        cur = self.conn.cursor()
        user_data = self.get_user_data(username)
        creator_id = user_data["user_id"]
        if user_data is not None and \
           user_data["is_examiner"] is True and \
           user_data["in_session"] is None:
            cur.execute(
                _queries['create_session'],
                (session_id, session_password, creator_id)
            )
            self.conn.commit()
            return {
                "session_id": session_id,
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
            dict, Session data or None if not available
        """

        cur = self.conn.cursor()
        cur.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
        sess_rows = cur.fetchall()

        cur = self.conn.cursor()
        cur.execute("SELECT * FROM users WHERE in_session = ?", (session_id,))
        user_rows = cur.fetchall()
        
        if not sess_rows or len(sess_rows) != 1:
            return None
        
        sess_row = sess_rows[0]
        sess_data = {
            "session_id": session_id,
            "password": sess_row[1],
            "creator_id": sess_row[2],
            "users": []
        }

        for row in user_rows:
            sess_data["users"].append({
                "user_id": row[0],
                "display_name": row[2],
                "initials": row[3],
                "is_examiner": bool(row[5]),
            })

        return sess_data


    def add_user_to_session(self, username, session_id, session_token):
        """
        Add a user to given session

        Args:
            username (str): Username
            session_id (str): Session ID
            session_token: (str): Session token
        
        Returns:
            bool, Success
        """

        user_data = self.get_user_data(username)
        session_data = self.get_session_data(session_id)
        if user_data is None or session_data is None:
            return False
        cur = self.conn.cursor()
        cur.execute(
            _queries['add_user_to_session'],
            (session_id, session_token, username)
        )
        self.conn.commit()
        return True
    

    def logout_user(self, username):
        """
        Add a user to given session

        Args:
            username (str): Username
            session_id (str): Session ID
            session_token: (str): Session token
        
        Returns:
            bool, Success
        """

        user_data = self.get_user_data(username)
        if user_data is None or session_data is None:
            return False
        cur = self.conn.cursor()
        cur.execute("""
            UPDATE users
            SET in_session = null ,
                session_token = null
            WHERE username = ? ;
        """, (username,))
        self.conn.commit()
        return (user_data["in_session"] is not None)