import sqlite3
from sqlite3 import Error

_queries = {
    'create_users_table': """
        CREATE TABLE IF NOT EXISTS users (
            id integer PRIMARY KEY AUTOINCREMENT,
            username text NOT NULL,
            password text NOT NULL,
            is_examiner integer DEFAULT 0 NOT NULL
        ); 
        """,

    'create_sessions_table': """
        CREATE TABLE IF NOT EXISTS sessions (
            id integer PRIMARY KEY,
            name text NOT NULL
        ); 
        """,

    'create_user': """
        INSERT INTO users
            (username, password, is_examiner)
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
            self.conn.commit()
        except Error as e:
            print(e)
    

    def create_user(self, username, password, is_examiner=False):
        """
        Create a user if does not exist
        
        Args:
            username (str): Username
            password (str): Password
            is_examiner (bool): Is examiner?
        
        Returns:
            int, User ID
        """

        cur = self.conn.cursor()
        if self.get_user_data(username) is None:
            is_examiner = int(is_examiner)
            cur.execute(_queries['create_user'], (username, password, is_examiner))
            self.conn.commit()


    def get_user_data(self, username):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        rows = cur.fetchall()
        if not rows:
            return None
        return rows[0]