from pgm.ui_util.db import Database
import pytest
import os

"""
 pytest ./pgm/tests/test_db.py
    -x to stop after error
    -s to print prints
    -v verbose
"""
@pytest.fixture
def db():
    database = Database("test.db")
    #database.create_tables()
    yield database
    database.close()
    if os.path.exists("test.db"):
        print("exist")
        os.remove("test.db")

def test_create_tables(db):
    assert db.show_tables() == [] 
    db.create_tables()
    assert db.show_tables() == ['users', 'sqlite_sequence', 'sessions', 'apps', 'app_contexts', 'captures']

def test_get_user(db):
    db.create_tables()
    assert db.get_user(1) == None
    db.add_user("test","test","test")
    tmp = db.get_user("test")[4]
    assert db.get_user("test") == (1,"test","test","test",tmp)



def test_add_user(db):
    db.create_tables()
    assert db.add_user("test","test@test","test") == True
    with pytest.raises(TypeError):
        assert db.add_user("test")
    with pytest.raises(TypeError):
        assert db.add_user(None,"test@test")

    assert db.add_user(None,None,"test") == False
    assert db.add_user(None,"test",None) == False
    assert db.add_user("test",None,None) == False

    assert db.add_user(None,"test","test") == False
    assert db.add_user("test",None,"test") == False

    # convert value into string : shall not pass !!!
    assert db.add_user(1,1,1) == True
    print(db.get_user(1))


    assert db.add_user(1,1,"test") == False
    assert db.add_user(1,"test",1) == False
    assert db.add_user("test",1,1) == False

    assert db.add_user("test",1,"test") == False
    assert db.add_user("test","test",1) == False
    assert db.add_user(1,"test","test") == False

    # already exist
    assert db.add_user("test","test","test") == False
    # would need to verify email 

def test_get_all_items_from_table(db):
    db.create_tables()
    #print(db.show_tables())
    assert db.get_all_items_from_table("users") == []
    db.add_user("test","test","test")
    tmp = db.get_user("test")[4]
    assert db.get_all_items_from_table("users") == [(1,"test","test","test",tmp)]
