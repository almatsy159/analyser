class Database:
    def __init__(self, db_name="app.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        try :
            cursor.execute("PRAGMA foreign_keys = ON;")
        except sqlite3.error as e:
            log("c",f"couldn't activate foreign key ! : {e}")

        cursor.execute("""CREATE TABLE IF NOT EXISTS users (
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
        #self.conn.commit()
        cursor.execute("""CREATE TABLE IF NOT EXISTS  apps(
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS app_contexts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    app_id INTEGER NOT NULL,
    key TEXT NOT NULL,
    value TEXT,
    FOREIGN KEY(app_id) REFERENCES apps(id) ON DELETE CASCADE
);""")
        #self.conn.commit()
        cursor.execute("""CREATE TABLE IF NOT EXISTS captures(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    app_id INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    lang TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
                    FOREIGN KEY (app_id) REFERENCES apps(id) ON DELETE CASCADE);""")
        try :
            self.conn.commit()
        except sqlite3.Error as e:
            log("c",f"couldn't commit to the database ! {e}")

    def get_last_id(self,cursor):
        try :
            last_id = cursor.lastrowid
            log("s",f"getted id : {last_id}")
            return last_id
        except sqlite3.Error as e:
            log("c",f"couldn't get the id ! {e}")
            return None
        

    def add_session(self, idu):
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO sessions (idu) VALUES (?)", (idu,))
            self.conn.commit()
            log("s","inserted session correctly")
            last_id = self.get_last_id()
            
        except sqlite3.IntegrityError as err:
            log("c",f"couldn't add session : {err}")
            last_id = None
        return last_id
    
    def add_user(self, idu, email, password):
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO users (idu, email, password) VALUES (?, ?, ?)", (idu, email, password))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    """
    def user_exist(self,idu):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE idu = ?" (idu,))
        try :
            cursor.fetchone()[0]
        except :
            print("true")
    """
    def verify_user(self, idu, password):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE idu = ? AND password = ?", (idu, password))
        return cursor.fetchone() is not None
        
            