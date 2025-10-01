from log import log,init_log
import sqlite3
import json

init_log()
default_user_id = "test" # same in the overlay !
default_user_mail = "test@test.test"
default_user_pwd = "test"



class Database:
    def __init__(self, db_name="app.db"):
        self.conn = sqlite3.connect(db_name)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        #self.create_tables()

    def show_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        res = []
        tables = cursor.fetchall()
        for t in tables:
            res.append(t[0])
        return res


    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                idu VARCHAR(100) NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                idu VARCHAR(100) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (idu) REFERENCES users(idu) ON DELETE CASCADE
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS apps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS app_contexts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app_id INTEGER NOT NULL,
                key TEXT NOT NULL,
                value TEXT,
                FOREIGN KEY(app_id) REFERENCES apps(id) ON DELETE CASCADE
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS captures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                app_id INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                id_user VARCHAR(100) NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
                FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE
            );
        """)
        self.conn.commit()

    def get_all_items_from_table(self,table):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {table}")
        return cursor.fetchall()

    def create_default_user(self,*args):
        if args :
            self.add_user(*args)
        if self.get_user(default_user_id) == None: 
            self.add_user(default_user_id,default_user_mail,default_user_pwd)

    # ---------------- USERS CRUD ----------------
    def add_user(self, idu, email, password):
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (idu, email, password) VALUES (?, ?, ?)",
                (idu, email, password)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_user(self, idu):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE idu = ?", (idu,))
        return cursor.fetchone()

    def update_user(self, idu, email=None, password=None):
        cursor = self.conn.cursor()
        if email:
            cursor.execute("UPDATE users SET email=? WHERE idu=?", (email, idu))
        if password:
            cursor.execute("UPDATE users SET password=? WHERE idu=?", (password, idu))
        self.conn.commit()

    def delete_user(self, idu):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM users WHERE idu=?", (idu,))
        self.conn.commit()

    def verify_user(self, idu, password):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE idu=? AND password=?", (idu, password))
        return cursor.fetchone() is not None

    def user_exist(self, idu):
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE idu=?", (idu,))
        return cursor.fetchone() is not None

    # ---------------- SESSIONS CRUD ----------------
    def add_session(self, idu):
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO sessions (idu) VALUES (?)", (idu,))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    def get_sessions(self, idu=None):
        cursor = self.conn.cursor()
        if idu:
            cursor.execute("SELECT * FROM sessions WHERE idu=?", (idu,))
        else:
            cursor.execute("SELECT * FROM sessions")
        return cursor.fetchall()
    
    def get_session(self,idu=None):
        # get new session
        sessions = self.get_sessions()
        max = 0
        for session_cols in sessions:
            #print(session_cols[0])
            if session_cols[0] > max:
                max = session_cols[0]
        return max


    def delete_session(self, session_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE id=?", (session_id,))
        self.conn.commit()

    # ---------------- APPS CRUD ----------------
    def add_app(self, name, description=None):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO apps (name, description) VALUES (?, ?)", (name, description))
        self.conn.commit()
        return cursor.lastrowid

    def get_apps(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM apps")
        return cursor.fetchall()
    
    def get_app(self,app_id=None,app_name=None):
        cursor = self.conn.cursor()
        err = None
        try :
            
            if app_id==None and app_name == None:
                return None
        
            elif app_id == None:
                # get app id by name
            
                cursor.execute("SELECT * FROM apps WHERE name = ?",(app_name,))
            elif app_name == None:
                # get app name by id
        
                cursor.execute("SELECT * FROM apps WHERE id = ?",(app_id,))
        except sqlite3.Error as err:
            log("w",f"cloudn't get the app and raised {err}")
        finally :
            if err != None:
                return None
            else:
                 return cursor.fetchone()

            

    def update_app(self, app_id, name=None, description=None):
        cursor = self.conn.cursor()
        if name:
            cursor.execute("UPDATE apps SET name=? WHERE id=?", (name, app_id))
        if description:
            cursor.execute("UPDATE apps SET description=? WHERE id=?", (description, app_id))
        self.conn.commit()

    def delete_app(self, app_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM apps WHERE id=?", (app_id,))
        self.conn.commit()

    # ---------------- APP CONTEXTS CRUD ----------------
    def add_app_context(self, app_id, key, value):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO app_contexts (app_id, key, value) VALUES (?, ?, ?)", (app_id, key, value))
        self.conn.commit()
        return cursor.lastrowid

    def get_app_contexts(self, app_id=None):
        cursor = self.conn.cursor()
        if app_id:
            cursor.execute("SELECT * FROM app_contexts WHERE app_id=?", (app_id,))
        else:
            cursor.execute("SELECT * FROM app_contexts")
        return cursor.fetchall()

    def update_app_context(self, context_id, key=None, value=None):
        cursor = self.conn.cursor()
        if key:
            cursor.execute("UPDATE app_contexts SET key=? WHERE id=?", (key, context_id))
        if value:
            cursor.execute("UPDATE app_contexts SET value=? WHERE id=?", (value, context_id))
        self.conn.commit()

    def delete_app_context(self, context_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM app_contexts WHERE id=?", (context_id,))
        self.conn.commit()

    # ---------------- CAPTURES CRUD ----------------
    def add_capture(self, session_id, app_id, user_id):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO captures (session_id, app_id, user_id) VALUES (?, ?, ?)",
            (session_id, app_id, user_id)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_captures(self, session_id=None, app_id=None,user_id=None):
        cursor = self.conn.cursor()
        query = "SELECT * FROM captures WHERE 1=1"
        params = []
        if session_id:
            query += " AND session_id=?"
            params.append(session_id)
        if app_id:
            query += " AND app_id=?"
            params.append(app_id)
        if user_id:
            query += " AND user_id=?"
            params.append(user_id)
        cursor.execute(query, tuple(params))
        return cursor.fetchall()

    def delete_capture(self, capture_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM captures WHERE id=?", (capture_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()

    def to_json(self):
        serializable = {k: (list(v) if isinstance(v, tuple) else v) for k,v in self.__dict__.items()}
        return json.dumps(serializable)


if __name__=="__main__":
    db = Database("main.db")
    db.create_tables()
    print(db.show_tables())