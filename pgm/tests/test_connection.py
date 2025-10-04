from pgm.ui_util.connection import LoginForm,NewUserForm,MainWindow,main
import pytest
from unittest.mock import MagicMock,patch
from PyQt5.QtWidgets import QStackedWidget ,QMessageBox
from PyQt5.QtCore import Qt

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_stacked():
    return MagicMock(spec=QStackedWidget)


@pytest.fixture
def login_form(qtbot, mock_db, mock_stacked):
    form = LoginForm(mock_stacked, mock_db)
    qtbot.addWidget(form)
    return form, mock_db, mock_stacked 

def test_login_success(qtbot, mock_db, mock_stacked):
    mock_db.verify_user.return_value = True
    login_form = LoginForm(mock_stacked, mock_db)
    qtbot.addWidget(login_form)
    
    qtbot.keyClicks(login_form.id_input, "test_user")
    qtbot.keyClicks(login_form.pwd_input, "secret")
    
    with patch.object(QMessageBox, 'information') as mock_info:
        qtbot.mouseClick(login_form.login_btn, Qt.MouseButton.LeftButton)
        
        mock_db.verify_user.assert_called_once_with("test_user", "secret")
        mock_stacked.close.assert_called_once()
        args = mock_info.call_args[0]
        assert "Welcome back, test_user!" in args[2]

def test_login_failure(qtbot, mock_db, mock_stacked):
    mock_db.verify_user.return_value = False
    login_form = LoginForm(mock_stacked, mock_db)
    qtbot.addWidget(login_form)
    
    qtbot.keyClicks(login_form.id_input, "wrong_user")
    qtbot.keyClicks(login_form.pwd_input, "wrong_pass")
    
    with patch.object(QMessageBox, 'warning') as mock_warn:
        qtbot.mouseClick(login_form.login_btn, Qt.MouseButton.LeftButton)
        
        mock_db.verify_user.assert_called_once_with("wrong_user", "wrong_pass")
        mock_stacked.close.assert_not_called()
        args = mock_warn.call_args[0]
        assert "Invalid email or password." in args[2]

def test_load_new_user_form(qtbot, mock_db, mock_stacked):
    login_form = LoginForm(mock_stacked, mock_db)
    qtbot.addWidget(login_form)
    
    qtbot.mouseClick(login_form.new_btn, Qt.MouseButton.LeftButton)
    mock_stacked.setCurrentIndex.assert_called_once_with(1)


@pytest.fixture
def registration_form(qtbot, mock_db, mock_stacked):

    form = NewUserForm(mock_stacked, mock_db)
    qtbot.addWidget(form)
    return form


def test_registration_without_idu(qtbot,mock_db,mock_stacked,registration_form):
    #registration_form = NewUserForm(mock_stacked,mock_db)
    #qtbot.addWidget(registration_form)
    
    qtbot.keyClicks(registration_form.email_input,"test@test.test")
    qtbot.keyClicks(registration_form.pwd_input,"test")
    with patch.object(QMessageBox,'warning') as mock_warn:
        qtbot.mouseClick(registration_form.register_btn,Qt.MouseButton.LeftButton)
        mock_stacked.setCurrentIndex.assert_not_called()
        mock_db.add_user.assert_not_called()

        args = mock_warn.call_args[0]
        assert "All fields are required." in args[2]

def test_registration_without_email(qtbot,mock_db,mock_stacked,registration_form):
    qtbot.keyClicks(registration_form.idu_input,"test")
    qtbot.keyClicks(registration_form.pwd_input,"test")
    with patch.object(QMessageBox,'warning') as mock_warn:
        qtbot.mouseClick(registration_form.register_btn,Qt.MouseButton.LeftButton)
        mock_stacked.setCurrentIndex.assert_not_called()
        mock_db.add_user.assert_not_called()

        args = mock_warn.call_args[0]
        assert "All fields are required." in args[2]

def test_registration_without_pwd(qtbot,mock_db,mock_stacked,registration_form):
    qtbot.keyClicks(registration_form.email_input,"test@test.test")
    qtbot.keyClicks(registration_form.idu_input,"test")
    with patch.object(QMessageBox,'warning') as mock_warn:
        qtbot.mouseClick(registration_form.register_btn,Qt.MouseButton.LeftButton)
        mock_stacked.setCurrentIndex.assert_not_called()
        mock_db.add_user.assert_not_called()

        args = mock_warn.call_args[0]
        assert "All fields are required." in args[2]

def test_registration_fail():
    pass

def test_registration_success():
    pass