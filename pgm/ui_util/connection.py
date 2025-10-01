import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QStackedWidget, QMessageBox
)

from db import Database as db

class Database:
    def __init__(self, db_name="app.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    idu TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
        """)
        self.conn.commit()

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


class LoginForm(QWidget):
    def __init__(self, stacked_widget, db):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.db = db

        layout = QVBoxLayout()

        # Email field
        self.id_label = QLabel("Id:")
        self.id_input = QLineEdit()
        layout.addWidget(self.id_label)
        layout.addWidget(self.id_input)

        # Password field
        self.pwd_label = QLabel("Password:")
        self.pwd_input = QLineEdit()
        self.pwd_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.pwd_label)
        layout.addWidget(self.pwd_input)

        # Buttons
        self.login_btn = QPushButton("Login")
        self.new_btn = QPushButton("New User")

        self.login_btn.clicked.connect(self.handle_login)
        self.new_btn.clicked.connect(self.load_new_user_form)

        layout.addWidget(self.login_btn)
        layout.addWidget(self.new_btn)

        self.setLayout(layout)

    def handle_login(self):
        idu = self.id_input.text()
        pwd = self.pwd_input.text()
        if self.db.verify_user(idu, pwd):
            QMessageBox.information(self, "Login", f"Welcome back, {idu}!")
            self.stacked_widget.idu = idu
            #self.close()
            self.stacked_widget.close()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid email or password.")
            return None

    def load_new_user_form(self):
        self.stacked_widget.setCurrentIndex(1)  # switch to new user form


class NewUserForm(QWidget):
    def __init__(self, stacked_widget, db):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.db = db

        layout = QVBoxLayout()

        # Name
        self.idu_label = QLabel("Id:")
        self.idu_input = QLineEdit()
        layout.addWidget(self.idu_label)
        layout.addWidget(self.idu_input)

        # Email
        self.email_label = QLabel("Email:")
        self.email_input = QLineEdit()
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_input)

        # Password
        self.pwd_label = QLabel("Password:")
        self.pwd_input = QLineEdit()
        self.pwd_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.pwd_label)
        layout.addWidget(self.pwd_input)

        # Register button
        self.register_btn = QPushButton("Register")
        self.register_btn.clicked.connect(self.handle_register)
        layout.addWidget(self.register_btn)

        # Back to login
        self.back_btn = QPushButton("Back to Login")
        self.back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        layout.addWidget(self.back_btn)

        self.setLayout(layout)

    def handle_register(self):
        idu = self.idu_input.text()
        email = self.email_input.text()
        pwd = self.pwd_input.text()

        if not idu or not email or not pwd:
            QMessageBox.warning(self, "Error", "All fields are required.")
            return

        success = self.db.add_user(idu, email, pwd)
        if success:
            QMessageBox.information(self, "Register", "New user created successfully!")
            self.stacked_widget.setCurrentIndex(0)
        else:
            QMessageBox.warning(self, "Error", "Email already exists. Choose another.")


class MainWindow(QStackedWidget):
    def __init__(self):
        super().__init__()
        #self.db = Database()
        self.db = db()
        self.idu = None
        self.state = False

        # Create forms
        self.login_form = LoginForm(self, self.db)
        self.new_user_form = NewUserForm(self, self.db)

        # Add widgets to stack
        self.addWidget(self.login_form)  # index 0
        self.addWidget(self.new_user_form)  # index 1

        self.setCurrentIndex(0)  # start with login form
    """
    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, "Quit", "Are you sure you want to quit?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.state = True
            event.accept()   # allow closing
        else:
            event.ignore()   # cancel closing
    """

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle("Connexion Form with SQLite")
    window.resize(300, 200)
    window.show()
    app.exec_()
    idu = window.idu
    app.quit()

    return idu


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle("Connexion Form with SQLite")
    window.resize(300, 200)
    window.show()
    app.exec_()
    print(window.idu)
    print(window.state)
    if window.idu != None:
        print(f"connected as {window.idu} launching app.")
    else :
        print("no user leaving app")
    sys.exit()
