import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy, QTabWidget, QListWidget, QMenuBar, QAction, QDockWidget,QMenu,QTreeWidget,QTreeWidgetItem
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject,QPoint
from PyQt5.QtGui import QFont
import subprocess
import requests
import re
from pynput import keyboard,mouse

import mss
import os
from datetime import datetime


import imageio.v3 as iio
import io
from PIL import Image

import queue
import threading

import json
import socket
import connection

import sqlite3

default_infos = {"title": "my article review","author":"glecomte","numbers":[0,1,2,3],"sub_dict":{"revelance":0,"global_score":0,"sub_list":[2,3,5,7,11]}}

controls = {"action":{keyboard.Key.ctrl,keyboard.Key.alt},
            "quit":{keyboard.Key.ctrl,keyboard.Key.esc}}

handler_addr = "http://localhost:5000/process_image"


class Database:
    def __init__(self, db_name="app.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")

        cursor.execute("""CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    idu TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
    idu VARCHAR(100) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (idu) REFERENCES users(id) ON DELETE CASCADE
);
        """)
        #self.conn.commit()
        cursor.execute("""CREATE TABLE IF NOT EXISTS  apps(
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
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
        self.conn.commit()

    def add_session(self, idu):
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO sessions (idu) VALUES (?)", (idu,))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_current_session(self,idu):
        try :
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM sessions")
            tmp = cursor.fetchall()
            print("tmp : ",tmp)
            cursor.execute("SELECT id FROM sessions WHERE idu = ? ORDER BY created_at DESC LIMIT 1;", (idu,))
            print(idu)
            res = cursor.fetchone()
            if res == None:
                res = 1
            else :
                res = res[0] +1

            print(f"current session : {res}")
            return res
        except sqlite3.IntegrityError:
            return False
    
def extract_application_from_window_name(context):
    print(context)

    print(context["window"]["name"])
    my_match = re.search(r'[-—]\s*([^—\-\n]+)\s*$', context["window"]["name"])
    
    if my_match : 
        #print("match : ",my_match.group(1))
        res = re.sub(" ","",my_match.group(1))
        #return my_match.group(1)mmmmmmm

    else :
        res = re.sub(" ","",context["window"]["name"])
    print(res)
    return res
    
# Worker thread
def worker(task_queue):
    while True:
        func, args = task_queue.get()
        try:
            print(f"executing {func}")
            func(*args)  # Execute the queued function
        except Exception as e:
            print("Error in queued task:", e)
        finally:
            task_queue.task_done()



def capture_window(window_info,context,process=None,save_dir="data/img"):

    """Capture la fenêtre active et enregistre l'image."""
    if not window_info:
        print("Aucune fenêtre active détectée.")
        return

    x, y = window_info["pos"]
    w, h = window_info["size"]

    # extract and save img

    os.makedirs(save_dir, exist_ok=True)
    filename_tmp = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    filename = os.path.join(save_dir, filename_tmp)

    if w ==0 or h ==0:
        print("capturing full window")
        with mss.mss() as sct:
            sct_img = sct.grab({"top":context["window"]["pos"][0],"left":context["window"]["pos"][1],"width":context["window"]["size"][0],"height":context["window"]["size"][1]})
            img = Image.frombytes("RGB",sct_img.size,sct_img.rgb)
            mss.tools.to_png(sct_img.rgb, sct_img.size, output=filename)
    else :
        with mss.mss() as sct:
            sct_img = sct.grab({"top": y, "left": x, "width": w, "height": h})
            img = Image.frombytes("RGB",sct_img.size,sct_img.rgb)
            mss.tools.to_png(sct_img.rgb, sct_img.size, output=filename)


        # default process for now
    sended = None
    if process == None:
        sended = send_image_to_handler(img,filename,context)
    else :
        sended = send_image_to_handler(img,filename,context,process)

    if sended == False:
        print("should save to send it later !(next connection ? pool_file ?)")

    return filename,save_dir

def send_image_to_handler(img,filename,context,process=[{"name":"test"}],handler_addr=handler_addr):
        
        flag = False
        buf = io.BytesIO()
        iio.imwrite(buf, img, format='PNG')
        buf.seek(0)
        files = {"image":(filename,buf,"image/png")}
        data = {"context":context,"process":process}
        try :
            response = requests.post(handler_addr,files=files,data=data)
            flag = True

        except :
            response = None
        finally :
            if response == None:
                print("connection couldn't be achieved : capture not")
            else:
                print("handler response:",response)

        return flag


def capture_info(first,second):
    pos = first[0] if first[0]<second[0] else second[0],first[1] if first[1]<second[1] else second[1]
    print(pos)
    size = abs(first[0]-second[0]),abs(first[1]-second[1])
    print(size)
    window_info = {"pos":pos,"size":size}
    return window_info

    #capture_window(window_info)


def wait_for_two_clicks():
    click_count = 0
    fisrt_click = None  
    second_click = None        
    def on_click(x, y, button, pressed):
        nonlocal click_count
        nonlocal fisrt_click
        nonlocal second_click
        if pressed:
            click_count += 1
            print(f"Click {click_count} at {(x, y)}")
            if click_count == 1:
                fisrt_click = x,y
            if click_count == 2:
                second_click = x,y
                return False   # stop listener

    listener = mouse.Listener(on_click=on_click)
    listener.start()
    listener.join() 
    return fisrt_click,second_click

def wait_for_action():
    print("in wait for action")
    key_pressed = None
    def on_press(key):
        nonlocal key_pressed
        key_pressed = key
        return False
 
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    listener.join()
    return key_pressed


def listen_keyboard(qwidget,task_queue,context):

    pressed = set()

    def change_mod():

        qwidget.comm.update_mod.emit()
        #to_print = {"mode : ":qwidget.mods[qwidget.mod]}
        #qwidget.comm.update_text.emit(to_print)

    def capture():
        first,second = wait_for_two_clicks()
        print(first)
        print(second)
        window_info = capture_info(first,second)
        task_queue.put((capture_window,(window_info,context)))



    def leave_app():
        qwidget.quit()

    def on_press(key):
        print(f"{key} pressed !")
        pressed.add(key)
        event("on press")

    def on_release(key):
        action_key = None
        
        if controls["quit"] == pressed:
            leave_app()
        elif controls["action"] == pressed:
            print("wait for action launched !")
            action_key = wait_for_action()
        if action_key:
            print(f"action {action_key} should be triggered")
            if action_key == keyboard.KeyCode.from_char("c"):
                capture()
            elif action_key == keyboard.KeyCode.from_char("m"):
                change_mod()
        pressed.discard(key)
        return context

    def event(e):
        to_print = {"last event : m":e}
        qwidget.comm.update_text.emit(to_print)
        ctx = event_appened(context,qwidget)
        qwidget.change_ctx(ctx)




    listener = keyboard.Listener(on_press=on_press,on_release=on_release)
    listener.start()

def listen_mouse(qwidget,task_queue,context):
    
    def on_move(x, y, injected):

        #print(f"Pointer mover to {x},{y},it was {'faked' if injected else 'not faked'}")
        event("on_move")

    def on_click(x, y, button, pressed, injected):

        #print(f"{pressed} at {x},{y} with {button} ,it was {'faked' if injected else 'not faked'}")
        event("on click")

    def on_scroll(x, y, dx, dy, injected):
       
        #print(f"Scrolled {'down' if dy<0 else 'up'} at {x},{y} for {dx},{dy} and it was {'faked' if injected else 'not faked'}")
        event("on_scroll")

    def event(e):
        #qwidget.text = e
        to_print = {"last event : ":e}
        qwidget.comm.update_text.emit(to_print)
        ctx = event_appened(context,qwidget)
        qwidget.change_ctx(ctx)
 
    # non-blocking fashion:
    listener = mouse.Listener(
        on_move=on_move,
        on_click=on_click,
        on_scroll=on_scroll)
    listener.start()
       
def event_appened(context,qwidget=None,to_print=False):
    # a bug with window name rn !!! may need to extract app from window name outside of this one !

    current = get_active_window()
    window_name = context["window_name"]
    if current != None:
        if current != context["window"]:
            print("window changed from :",context["window"],"\nto :",current)
            context["window"]= current
            print(context["window_name"])
            
            window_name = extract_application_from_window_name(context)
            context["window_name"] = window_name
            print(context["window_name"])

            to_display = {"window name : ":window_name}
            qwidget.comm.update_text.emit(to_display)
            qwidget.change_ctx(context)

    return context
            

def get_active_window():
    """Retourne le nom et la géométrie (x, y, w, h) de la fenêtre active."""
    try:
        # ID de la fenêtre active
        
        wid = subprocess.check_output(["xdotool", "getactivewindow"]).decode().strip()
        # Nom de la fenêtre
        name = subprocess.check_output(["xdotool", "getwindowname", wid]).decode().strip()

        # Géométrie de la fenêtre
        geom = subprocess.check_output(["xdotool", "getwindowgeometry", wid]).decode()

        pos, size = None, None
        for line in geom.splitlines():
            if "Position" in line:
                pos = tuple(map(int, line.split()[1].split(',')))
            if "Geometry" in line:
                size = tuple(map(int, line.split()[1].split('x')))

        return {"id": wid, "name": name, "pos": pos, "size": size}
    except subprocess.CalledProcessError:
        return None


class Communicate(QObject):

    update_text = pyqtSignal(dict)
    update_mod = pyqtSignal()
    update_infos = pyqtSignal(dict)


class DisplayInfo(QWidget):
    def __init__(self,infos=None,parent=None):

        super().__init__(parent)
        
        self.setGeometry(500,500,500,500)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        #self.setAttribute(Qt.WA_TransparentForMouseEvents,True)
        
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(5)
        self.setLayout(self.main_layout)
        
        if infos == None:
            self.infos = {}
        else:
            self.infos = {}
        self.generate_view(default_infos)
        
        self.adjustSize()
        self._drag_active = False
        self._drag_position = QPoint()



    def create_info_widget(self, my_dict=None,previous_layout=None):
        print(my_dict)
        if my_dict is None:
            my_dict = {}

        # Container for all lines
        container_widget = QWidget(self)
        #container_widget.setAttribute(Qt.WA_TransparentForMouseEvents,True)
        container_layout = QVBoxLayout(container_widget)
        container_layout.setSpacing(5)

        for k, v in my_dict.items():
            # Layout for this line
            line_layout = QHBoxLayout()
            line_layout.setSpacing(10)
            

            # Key label
            key_label = QLabel(str(k),self)
            key_label.setAttribute(Qt.WA_TransparentForMouseEvents)
            key_font = QFont("Segoe UI", 10, QFont.Bold)
            key_label.setFont(key_font)
            key_label.setStyleSheet("color: #00aaff;")
            key_label.adjustSize()
            line_layout.addWidget(key_label)

            # Value or nested dict
            if isinstance(v, dict):
                # Recursively create sub-widgets for the nested dict
                sub_widget = self.create_info_widget(v)
                line_layout.addWidget(sub_widget)
            else:
                value_label = QLabel(str(v),self)
                value_label.setAttribute(Qt.WA_TransparentForMouseEvents)
                value_font = QFont("Consolas", 10)
                value_label.setFont(value_font)
                value_label.setStyleSheet("color: white;")
                value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                line_layout.addWidget(value_label)

            line_layout.addStretch()

            # Line container widget
            line_widget = QWidget(self)
            line_widget.setAttribute(Qt.WA_TransparentForMouseEvents,True)
            line_widget.setLayout(line_layout)
            line_widget.setStyleSheet("""
                background-color: rgba(0, 0, 100, 150);
                border-radius: 6px;
            """)
            line_widget.adjustSize()
            # Add line to main container
            container_layout.addWidget(line_widget)

        return container_widget
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_active = True
            self._drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_active and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_active = False

    
    def generate_view(self, info_dict=None):
        if info_dict == None:
            info_dict = self.infos
        # Clear previous widgets
        while self.main_layout.count():
            child = self.main_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        info_widget = self.create_info_widget(info_dict)
        self.main_layout.addWidget(info_widget)
        self.adjustSize()
        self.show()

    def set_infos(self,infos=None):
        self.infos = infos
        self.generate_view()



class SocketServerThread(threading.Thread):
    def __init__(self, host='127.0.0.1', port=5002, callback=None):
        super().__init__()
        self.host = host
        self.port = port
        self.callback = callback
        self.daemon = True  # Le thread s'arrête avec l'UI

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            while True:
                conn, addr = s.accept()
                with conn:
                    data = conn.recv(1024)
                    if data:
                        #data = data.decode()
                        print("recived from handler : ",data)
                        if self.callback:
                            print(data.decode())
                            data = json.loads(data.decode())
                            print(data)
                            # data should be formated this way in handler {"from_server":{"message":x,"wait_for":y},"result":{json}to parse it (method in overlay)
                            self.callback(data)
                            
                        


class Overlay(QWidget):
    def __init__(self,context, text="Overlay HUD", x=100, y=100, w=400, h=400,display_dict=None):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)

        #self.setWindowFlag(Qt.WindowStaysOnTopHint)
        #self.setWindowFlag(Qt.FramelessWindowHint)
        #self.setWindowFlag(Qt.Tool)
        

        screen = QApplication.primaryScreen()
        size = screen.size()
        self.w = size.width()
        self.h = size.height()
        self.setAttribute(Qt.WA_TransparentForMouseEvents,True)  # Click-through
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.text = text
        self.display_dict = display_dict
        
        
        self.comm = Communicate()
        
        self.comm.update_text.connect(self.set_text2)
        self.comm.update_mod.connect(self.change_mod)
        self.comm.update_infos.connect(self.set_display_widget_infos)


        self.context = context
        
        self.db = Database()
        self.db.add_session(context["user"])
        self.id_session = self.db.get_current_session(context["user"])
        self.context["session"] = self.id_session
        
        
        self.server_thread = SocketServerThread(callback=self.comm.update_infos.emit)

        self.server_thread.start()
       
        
        self.info_widget = DisplayInfo(default_infos,self)
        self.label = QLabel(self.text, self)
        self.label.setWordWrap(True)
        self.label.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.label.setFont(QFont("Arial", 20))
        self.label.setStyleSheet("color: red; background-color: rgba(0,0,0,100);")
        self.label.setAlignment(Qt.AlignCenter)

        self.colors = ["red","blue","green"]
        self.mod = 0
        self.mods= {0:"partial",1:"passive",2:"full"}

        self.create_interface()
        self.generate_interface()

    def get_display_dict_str(self):
        res = ""
        for k,v in self.display_dict.items():
            res += f"{k} : {v}\n"
        return res


    def change_mod(self):

        self.mod = (self.mod+1) % len(self.colors)
        self.display_dict["mode : "] = self.mod
        self.generate_interface()

    def create_interface(self):
        #self.menubar = QMenuBar(self)
        #self.label = QLabel(self.get_display_dict_str(),self)
        #self.label.setFont(QFont("Arial", 20))
        #self.session_list = QListWidget(self)
        #self.tabs = QTabWidget(self)
        self.fullmode = FullModeApp()

    def generate_interface(self):

        print("generating interface ")
        
        color = self.colors[self.mod]
        self.label.deleteLater()
        self.label = QLabel(self.get_display_dict_str())
        self.label.setFont(QFont("Arial", 10))
        self.label.setStyleSheet(f"color: {color}; background-color: rgba(0,0,0,100);")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.adjustSize()
        self.label.show()
        #self.label.adjustSize()

        mod = self.mods[self.mod]
        """
        if mod == "partial":
            #overlay
            self.setAttribute(Qt.WA_TransparentForMouseEvents,False) 

            #info_widget
            self.info_widget.show()
            self.info_widget.move(100, 500)        # position inside overlay
            self.info_widget.adjustSize()
            self.info_widget.setAttribute(Qt.WA_TransparentForMouseEvents,False) 
            for c in self.info_widget.findChildren(QWidget):
                c.setAttribute(Qt.WA_TransparentForMouseEvents,False)
            self.info_widget.show()
            self.label.show()
        elif mod == "passive":
            #overlay
            self.setAttribute(Qt.WA_TransparentForMouseEvents,True) 

            #infowidget
            
            self.info_widget.setAttribute(Qt.WA_TransparentForMouseEvents,True)
            for c in self.info_widget.findChildren(QWidget):
                c.setAttribute(Qt.WA_TransparentForMouseEvents,True)
            self.info_widget.show()
            self.label.show()
        else :

            self.info_widget.hide()
            self.label.show()
            #self.label.hide()
        """
        if mod== "partial" :
            self.setup_partial_mode()
        elif mod == "full":
            self.setup_full_mode()
        elif mod == "passive":
            self.setup_passive_mod()

    def setup_passive_mod(self):
         #overlay
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TransparentForMouseEvents,True) 

        #infowidget
            
        self.info_widget.setAttribute(Qt.WA_TransparentForMouseEvents,True)
        for c in self.info_widget.findChildren(QWidget):
            c.setAttribute(Qt.WA_TransparentForMouseEvents,True)

        self.info_widget.show()
        self.label.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.label.setWindowFlag(Qt.FramelessWindowHint)
        self.label.show()
        #self.label.adjustSize()
        self.fullmode.hide()

    def setup_partial_mode(self):
        #self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TransparentForMouseEvents,False) 
        for c in self.info_widget.findChildren(QWidget):
            c.setAttribute(Qt.WA_TransparentForMouseEvents,False)
        #self.label.adjustSize()
        self.label.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.label.setWindowFlag(Qt.FramelessWindowHint)
        self.label.show()
        
        self.info_widget.show()
        self.fullmode.hide()
        

    def setup_full_mode(self):
         # Menu bar
        #self.setWindowFlag(Qt.Tool)
        #self.fullmode.setWindowFlag(Qt.Window)
        #self.fullmode.show()
        self.fullmode.showMaximized()
        self.info_widget.hide()



    def set_text2(self,dict,color=None):
        #print(self.display_dict)
        #if color == None:
        #    color = self.colors[self.mod]
        
        res = ""
        for k,v in dict.items():
            self.display_dict[k] = v
        for k,v in self.display_dict.items():
            res += f"{k} : {v}\n"
        #print(self.display_dict)mm

        self.label.setText(res)
        #self.label.setStyleSheet(f"color: {color}; background-color: rgba(0,0,0,100);")
        #self.label.adjustSize()

    def set_display_widget_infos(self,infos):
        print("in infos :",infos)
        self.info_widget.set_infos(infos)
        self.generate_interface()

    def parse_display_widget_infos(self,infos):
        data = infos["result"]
        status = infos["from_server"]
        if status["wait_for"] == 0 :
            print("no waiting for more so update display")
            self.set_display_widget_infos(data)
        elif status["wait_for"] >= status["message"]:
            print(f"message n_{status['message']} over a total of {status['wait_for']}")
            infos = self.info_widget.infos
            for k,v in data.items():
                infos[k] = v
            self.set_display_widget_infos(infos)
        self.generate_interface()

    def change_ctx(self,ctx):
        self.context = ctx

    def keyPressEvent(self, event):

        if event.key == Qt.Key_Escape:
            QApplication.quit()
        
    def quit(self):
        QApplication.quit()


class FullModeApp(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Full Mode App")
        #self.resize(1000, 600)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        # Main layout (vertical)
        main_layout = QVBoxLayout(self)

        # ---- MenuBar ----
        self.menu_bar = QMenuBar()
        file_menu = QMenu("File", self)
        edit_menu = QMenu("Edit", self)
        help_menu = QMenu("Help", self)

        # Example actions
        new_action = QAction("New Session", self)
        new_action.triggered.connect(self.new_session)

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)

        file_menu.addAction(new_action)
        file_menu.addAction(quit_action)

        edit_menu.addAction(QAction("Preferences", self))
        help_menu.addAction(QAction("About", self))

        self.menu_bar.addMenu(file_menu)
        self.menu_bar.addMenu(edit_menu)
        self.menu_bar.addMenu(help_menu)

        main_layout.setMenuBar(self.menu_bar)

        # ---- Central HBox ----
        central_layout = QHBoxLayout()

        # Left: sessions & captures tree view
        self.session_tree = QTreeWidget()
        self.session_tree.setHeaderHidden(True)
        self.session_tree.itemDoubleClicked.connect(self.open_analysis)

        # Example sessions/captures
        session1 = QTreeWidgetItem(["Session 1"])
        QTreeWidgetItem(session1, ["Capture A"])
        QTreeWidgetItem(session1, ["Capture B"])

        session2 = QTreeWidgetItem(["Session 2"])
        QTreeWidgetItem(session2, ["Capture X"])
        QTreeWidgetItem(session2, ["Capture Y"])

        self.session_tree.addTopLevelItem(session1)
        self.session_tree.addTopLevelItem(session2)

        self.session_tree.expandAll()

        central_layout.addWidget(self.session_tree, 1)

        # Right: main tab area (with closable tabs)
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        central_layout.addWidget(self.tab_widget, 3)

        main_layout.addLayout(central_layout)

    # ---- Functions ----
    def new_session(self):
        print("New session triggered")

    def open_analysis(self, item, column):
        if item.parent() is None:
            # Ignore top-level (sessions), only open captures
            return
        analysis_name = f"{item.parent().text(0)} - {item.text(0)}"
        tab = QLabel(f"Content of {analysis_name}")
        self.tab_widget.addTab(tab, analysis_name)
        self.tab_widget.setCurrentWidget(tab)

    def close_tab(self, index):
        widget = self.tab_widget.widget(index)
        if widget:
            self.tab_widget.removeTab(index)
            widget.deleteLater()


def main(window,user_id="test"):
    # Global task queue
    task_queue = queue.Queue()

    # Start the worker thread
    threading.Thread(target=worker, daemon=True,args=(task_queue,)).start()

    context = {"window":window,"user":user_id}
    window_name = extract_application_from_window_name(context)
    context["window_name"] = window_name

    print(window)

    if window:
        print(f"Fenêtre active : {window['name']} ({window['size'][0]}x{window['size'][1]})")
        app_qt = QApplication(sys.argv)
        overlay = Overlay(text=f"{context['window']['name']}", x=1400, y=600,context=context,display_dict={"window_name":context['window']['name']})
        listen_keyboard(overlay,task_queue,context)
        listen_mouse(overlay,task_queue,context)
        overlay.show()
        
        sys.exit(app_qt.exec_())
    else:
        print("Impossible d'obtenir la fenêtre active.")

if __name__=="__main__":
    window = get_active_window()
    user_id = connection.main()
    if user_id != None:
        main(window,user_id)
    else :
        main(window)