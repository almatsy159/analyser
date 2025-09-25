from ui_util.db import Database
import pytest
import os

@pytest.fixture
def db():
    database = Database("test.db")
    yield database
    database.close()
    if os.path.exists("test.db"):
        print("exist")
        os.remove("test.db")

def test_create_tables(db):
    assert db.show_tables == []
    db.create_tables()
    assert db.show_tables() == ['users', 'sqlite_sequence', 'sessions', 'apps', 'app_contexts', 'captures']

def test_add_user(db):
    pass