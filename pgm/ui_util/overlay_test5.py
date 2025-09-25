import sys
from PyQt5.QtWidgets import QApplication, QLabel,QLineEdit, QWidget, QToolButton,QVBoxLayout, QHBoxLayout, QSizePolicy, QTabWidget, QListWidget, QMenuBar, QAction, QDockWidget,QMenu,QTreeWidget,QTreeWidgetItem
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

#import sqlite3
#from loguru import logger
from pgm.ui_util.log import log,init_log
from pgm.ui_util.db import Database
import pgm.contract

init_log()

default_infos = {"title": "my article review","author":"glecomte","numbers":[0,1,2,3],"sub_dict":{"revelance":0,"global_score":0,"sub_list":[2,3,5,7,11]}}
default_infos2 = {"window_name": "default","user":"default"}
controls = {"action":{keyboard.Key.ctrl,keyboard.Key.alt},
            "quit":{keyboard.Key.ctrl,keyboard.Key.esc}}

handler_addr = "http://localhost:5000/process_image"
handler_portal = "http://localhost:5000/portal"

    
def extract_application_from_window_name(context):
    log("i",f"{context}")

    log("i",f"{context['window']['name']}")
    my_match = re.search(r'[-—]\s*([^—\-\n]+)\s*$', context["window"]["name"])
    
    if my_match : 
        #log("match : ",my_match.group(1))
        res = re.sub(" ","",my_match.group(1))
        #return my_match.group(1)

    else :
        res = re.sub(" ","",context["window"]["name"])
    if res :
        log("s",res)
    else :
        log("c","no result out of the window name !")
    return res
    
# Worker thread
def worker(task_queue):
    while True:
        #log("d",f"{task_queue}")
        func, args = task_queue.get()
        flag = False
        err = None
        try:
            log(f"executing {func}")
            func(*args)  # Execute the queued function
            flag  = True
            log("s",f"ended try block ! flag should be true : {flag}")
        except Exception as e:
            err = e
            log("Error in queued task:", e)
        finally:
            task_queue.task_done()
            if flag == False:
                log("w",f"couldn't do the task {task_queue} : {func} : {err}")
            else :
                log("s",f"task {task_queue}: {func} effectued successfully")


class Capture:
    def __init__(self,user,session,window_name,timestamp,pos,size,context,ext="png",save=True,f_dir="data/img"):
        self.context = context
        self.user = user
        self.session = session
        self.window_name = window_name
        self.timestamp = timestamp
        self.dir = f_dir
        #self.img = img
        self.pos = pos
        self.size = size
        self.ext = ext
        self.filename = f"{self.user}_{self.session}_{self.window_name}_{self.timestamp}.{self.ext}"
        self.f_path = os.path.join(self.dir, self.filename)
        if self.size[0] == 0 or self.size[1] == 0:
            self.size = self.context.window["pos"][0],self.context.window["pos"][1]
        self.w,self.h = self.size[0],self.size[1]
        self.x,self.y = self.pos[0],self.pos[1]
        
        self.img = None
        self.sct_img = None
        # default idc (id capture) and app_id while both are not implemented properly
        # write capture into db => get_id .
        self.idc = 0 
        self.app_id = 0

        self.save = save
        
        self.capture()

    def capture(self,a1=None,a2=None,*args):
        with mss.mss() as sct:
            self.sct_img = sct.grab({"top":self.y,"left":self.x,"width":self.w,"height":self.h})
            self.img = Image.frombytes("RGB",self.sct_img.size,self.sct_img.rgb)
            if self.save :
                mss.tools.to_png(self.sct_img.rgb, self.sct_img.size, output=self.f_path)
            
            #self.context.db.add_capture()
    def write_into_db(self):
        # to edit both here and db ...
        self.context.db.add_capture(self.session,self.app)
        self.idc = self.context.db.get_capture()
    
    def add_to_sender(self,sender):
        sender.add_capture(self.idc,self.app_id)
          

class Sender:
    sid = 0
    def __init__(self,context,process="default",addr=handler_portal):
        self.captures = {}
        self.process = process
        self.addr = addr
        self.context = context
        self.sender_id = Sender.sid
        self.sender_id2 = self.sid
        Sender.sid += 1
        log("d",f"global sid : {Sender.sid} , sid : {self.sender_id} , self sid : {self.sid}, sid2 : {self.sender_id2}") 
        self.sid += 1
        log("d",f"global sid : {Sender.sid} , sid : {self.sender_id} , self sid : {self.sid}, sid2 : {self.sender_id2}") 
    
    def add_capture(self,id_capture,capture):
        self.captures[id_capture] = capture
    
    def send_capture(self,capture,cid=None):

        buf = io.BytesIO()
        iio.imwrite(buf, capture.img, format='PNG')
        buf.seek(0)
        files = {"image":(capture.f_path,buf,f"image/{capture.ext}")}
        data = {"context":self.context.to_json(),"process":self.process,"sid":[self.sender_id,self.sender_id2],"cid":cid}
        flag = False
        try :
            response = requests.post(handler_addr,files=files,data=data)
            flag = True

        except :
            response = None
        finally :
            if flag == False:
                log("w","connection couldn't be achieved : capture not sended")
            else:
                log("s",f"handler response: {response}")

        #return flag
    
    def send_all(self,a1=None,a2=None,*args):
        cpt = 0
        total = {"True":0,"False":0}
        for cid,c in self.captures.items():
            cpt +=1
            self.send_capture(c,cid)
            #print(res)
            #total[res] +=1
        #print(total)
        #return total


def capture_window(window_info,context,process=None,save_dir="data/img"):
    log("d",f"context : {context},\nwindow_ifno : {window_info}")

    """Capture la fenêtre active et enregistre l'image."""
    if not window_info:
        log("c","Aucune fenêtre active détectée.")
        return

    x, y = window_info["pos"]
    w, h = window_info["size"]
    pos = (x,y)
    size = (w,h)

    # extract and save img

    os.makedirs(save_dir, exist_ok=True)
    filename_tmp = f"{context.user}_{context.session}_{context.window_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    filename = os.path.join(save_dir, filename_tmp)

    if w ==0 or h ==0:
        log("w","capturing full window")
        with mss.mss() as sct:
            sct_img = sct.grab({"top":context.window["pos"][0],"left":context.window["pos"][1],"width":context.window["size"][0],"height":context.window["size"][1]})
            img = Image.frombytes("RGB",sct_img.size,sct_img.rgb)
            mss.tools.to_png(sct_img.rgb, sct_img.size, output=filename)
    else :
        log("s",f"capturing window and saving it as {filename} into {save_dir}")
        with mss.mss() as sct:
            sct_img = sct.grab({"top": y, "left": x, "width": w, "height": h})
            img = Image.frombytes("RGB",sct_img.size,sct_img.rgb)
            mss.tools.to_png(sct_img.rgb, sct_img.size, output=filename)


        # default process for now
    sended = None
    if process == None:
        log("i","no special process : default process applied")
        sended = send_image_to_handler(img,filename,context.to_json())
    else :
        log("i",f"special process {process}")
        sended = send_image_to_handler(img,filename,context.to_json(),process)

    if sended == False:
        log("c","couldn't send the image !should save to send it later !(next connection ? pool_file ?)")

    return filename,save_dir

def send_image_to_handler(img,filename,context,process=[{"name":"test"}],handler_addr=handler_addr):
        
        flag = False
        buf = io.BytesIO()
        iio.imwrite(buf, img, format='PNG')
        buf.seek(0)
        files = {"image":(filename,buf,"image/png")}
        data = {"context":context.to_json(),"process":process}
        try :
            response = requests.post(handler_addr,files=files,data=data)
            flag = True

        except :
            response = None
        finally :
            if flag == False:
                log("w","connection couldn't be achieved : capture not sended")
            else:
                log("s","handler response:",response)

        return flag


def capture_info(first,second):
    pos = first[0] if first[0]<second[0] else second[0],first[1] if first[1]<second[1] else second[1]
    log("i",f"pos :{pos}")
    size = abs(first[0]-second[0]),abs(first[1]-second[1])
    log("i",f"size :{size}")
    window_info = {"pos":pos,"size":size}
    return window_info

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
            log("i",f"Click {click_count} at {(x, y)}")
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
    log("i","in wait for action")
    key_pressed = None
    def on_press(key):
        nonlocal key_pressed
        key_pressed = key
        log("s",f"key pressed :{key_pressed}")
        return False
 
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    listener.join()
    return key_pressed

def listen_keyboard(qwidget,task_queue,context):

    pressed = set()

    def change_mod():
        log("i","changing mode")
        qwidget.comm.update_mod.emit()
        #to_print = {"mode : ":qwidget.mods[qwidget.mod]}
        #qwidget.comm.update_text.emit(to_print)

    def capture():
        first,second = wait_for_two_clicks()
        log("s",f"first : {first} ; second : {second}")
        window_info = capture_info(first,second)
        log("s",f"window info {window_info}")
        # tmp comment to test Sender/Capture
        #task_queue.put((capture_window,(window_info,context)))
        cap = Capture(context.user,context.session,context.window_name,datetime.now(),window_info["pos"],window_info["size"],context)
        sender = Sender(context)
        task_queue.put((cap.capture,("args to test","arg2 to test")))
        #cap.add_to_sender(sender)
        sender.add_capture(cap.idc,cap)
        log("d",f"sender captures {sender.captures}")
        task_queue.put((sender.send_all,("arg1","arg2")))





    def leave_app():
        qwidget.quit()

    def on_press(key):
        log("i",f"key pressed : {key}")
        pressed.add(key)
        event("on_press")


    def on_release(key):
        action_key = None
        
        if controls["quit"] == pressed:
            leave_app()
        elif controls["action"] == pressed:
            log("d","wait for action launched !")
            action_key = wait_for_action()
        if action_key:
            log("d",f"action {action_key} should be triggered")
            if action_key == keyboard.KeyCode.from_char("c"):
                capture()
            elif action_key == keyboard.KeyCode.from_char("m"):
                change_mod()
        pressed.discard(key)
        return context

    def event(e):
        to_print = {"last event":e}
        qwidget.comm.update_text.emit(to_print)
        ctx = event_appened(context,qwidget)
        qwidget.change_ctx(ctx)




    listener = keyboard.Listener(on_press=on_press,on_release=on_release)
    listener.start()

def listen_mouse(qwidget,task_queue,context):
    
    def on_move(x, y, injected):

        #log(f"Pointer mover to {x},{y},it was {'faked' if injected else 'not faked'}")
        #event("on_move")
        pass

    def on_click(x, y, button, pressed, injected):

        #log(f"{pressed} at {x},{y} with {button} ,it was {'faked' if injected else 'not faked'}")
        #event("on click")
        pass

    def on_scroll(x, y, dx, dy, injected):
       
        #log(f"Scrolled {'down' if dy<0 else 'up'} at {x},{y} for {dx},{dy} and it was {'faked' if injected else 'not faked'}")
        #event("on_scroll")
        pass

    def event(e):
        #qwidget.text = e
        to_print = {"last event":e}
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
    current = get_active_window()
    if current != None:
        if current != context.window:
            log("i",f"window changed from : {context.window}\nto :{current}")
            context.change_window(current)
  
            window_name = context.window_name
            to_display = {"window name : ":window_name}
            qwidget.comm.update_text.emit(to_display)
            context = qwidget.change_ctx(context)

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
    def __init__(self,infos=None,parent=None,xi=500,yi=500,w=500,h=500):

        super().__init__(parent)
        self.h = h
        self.w = w
        self.xi = xi
        self.yi = yi
        
        self.setGeometry(self.xi,self.yi,self.w,self.h)
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
            self.infos = infos
        self.generate_view(self.infos)
        
        self.adjustSize()
        self._drag_active = False
        self._drag_position = QPoint()

    def create_info_widget(self, my_dict=None, previous_layout=None):
        if my_dict is None:
            my_dict = {}

        container_widget = QWidget(self)
        container_layout = QVBoxLayout(container_widget)
        #container_layout.setSpacing(5)

        for k, v in my_dict.items():
            line_widget = QWidget(self)
            line_layout = QVBoxLayout(line_widget)
            line_layout.setSpacing(2)

            if isinstance(v, dict):
                # Create a collapsible button for nested dictionaries
                toggle_button = QToolButton(self)
                toggle_button.setStyleSheet("color: #00aaff; font-weight: bold;")
                toggle_button.setText(str(k))
                toggle_button.setCheckable(True)
                toggle_button.setChecked(False)
                toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
                toggle_button.setArrowType(Qt.RightArrow)

                # Sub-widget for nested content
                sub_widget = self.create_info_widget(v)
                sub_widget.setVisible(False)  # start collapsed

            # Connect toggle
                def on_toggle(checked, widget=sub_widget, button=toggle_button):
                    widget.setVisible(checked)
                    button.setArrowType(Qt.DownArrow if checked else Qt.RightArrow)

                toggle_button.toggled.connect(on_toggle)

                line_layout.addWidget(toggle_button)
                line_layout.addWidget(sub_widget)
            else:
                # Regular key-value line
                h_layout = QHBoxLayout()
                key_label = QLabel(str(k), self)
                key_label.setStyleSheet("color: #00aaff; font-weight: bold;")
                value_label = QLabel(str(v), self)
                value_label.setStyleSheet("color: white;")
                value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                h_layout.addWidget(key_label)
                h_layout.addWidget(value_label)
                #h_layout.addStretch()
                line_layout.addLayout(h_layout)

            #line_layout.addStretch()

            # Line container widget
            line_widget = QWidget(self)
            #line_widget.setAttribute(Qt.WA_TransparentForMouseEvents,True)
            line_widget.setLayout(line_layout)
            line_widget.setStyleSheet("""
                background-color: rgba(0, 0, 100, 150);
                border-radius: 6px;
            """)
            #line_widget.adjustSize()
            #container_widget.adjustSize()
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
                        log("s",f"recived from handler : {data}")
                        if self.callback:
                            log("i",f"data_decoded : {data.decode()}")
                            data_json_decoded = json.loads(data.decode())
                            log("i",f"{data_json_decoded}")
                            # try get ifno from data or create a reciever !!
                            # data should be formated this way in handler {"from_server":{"message":x,"wait_for":y},"result":{json}to parse it (method in overlay)
                            self.callback(data_json_decoded)
                            
                        
class Overlay(QWidget):
    def __init__(self,context,db=None, text="Overlay HUD", x=100, y=100, w=400, h=400,display_dict=None):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)

        screen = QApplication.primaryScreen()
        size = screen.size()
        self.w = size.width()
        self.h = size.height()
        #self.setAttribute(Qt.WA_TransparentForMouseEvents,True)  # Click-through
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.text = text
        self.display_dict = display_dict
        
        
        self.comm = Communicate()
        
        self.comm.update_text.connect(self.set_text2)
        self.comm.update_mod.connect(self.change_mod)
        self.comm.update_infos.connect(self.set_display_widget_infos)


        self.context = context
        
        #self.db = db
        self.db = Database()
        self.db.create_tables()
        
        self.db.add_session(self.context.user)
        log("d",f"sessions : {self.db.get_all_items_from_table('sessions')}")
        self.id_session= self.db.get_session(self.context.user)
 
        if self.id_session == None:
            log("w","default session id loaded (0)")
            self.id_session = 0
        else :
            log("s",f"session id = {self.id_session}")
        self.context.session = self.id_session
        
        
        self.server_thread = SocketServerThread(callback=self.comm.update_infos.emit)
        self.server_thread.start()
       
        
        self.info_widget = DisplayInfo(default_infos)
        self.info_widget2 = DisplayInfo(default_infos2)
        #self.info_widget2.setAttribute(Qt.WA_TransparentForMouseEvents,False)

        self.colors = ["red","blue","green"]
        self.mod = 0
        self.mods= {0:"partial",1:"full"}

        self.create_interface()
        self.generate_interface()

    def get_display_dict_str(self):
        res = ""
        for k,v in self.display_dict.items():
            res += f"{k} : {v}\n"
        return res


    def change_mod(self):

        self.mod = (self.mod+1) % len(self.mods)
        self.display_dict["mode"] = self.mod
        self.generate_interface()

    def create_interface(self):
        self.fullmode = FullModeApp()

    def generate_interface(self):

        mod = self.mods[self.mod]
    
        if mod == "partial" :
            self.setup_partial_mode()
        elif mod == "full":
            self.setup_full_mode()


    def setup_partial_mode(self):
        """
        self.setAttribute(Qt.WA_TransparentForMouseEvents,False) 
        for c in self.info_widget.findChildren(QWidget):
            c.setAttribute(Qt.WA_TransparentForMouseEvents,False)
        for c in self.info_widget2.findChildren(QWidget):
            c.setAttribute(Qt.WA_TransparentForMouseEvents,False)
        """
        self.fullmode.hide()
        self.info_widget.show()
        self.info_widget2.show()
        
        

    def setup_full_mode(self):
         # Menu bar
        self.fullmode.activateWindow()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)

        for c in self.fullmode.findChildren(QWidget):
            c.setAttribute(Qt.WA_TransparentForMouseEvents,False)
        self.fullmode.showMaximized()
        self.info_widget.hide()
        self.info_widget2.hide()

    def set_text2(self,dict,color=None):
        for k,v in dict.items():
            self.display_dict[k] = v

        self.info_widget2.set_infos(self.display_dict)
        self.generate_interface()

    def set_display_widget_infos(self,infos):
        log("d",f"in infos :{infos}")
        self.info_widget.set_infos(infos)
        self.generate_interface()

    def parse_display_widget_infos(self,infos):
        data = infos["result"]
        status = infos["from_server"]
        if status["wait_for"] == 0 :
            log("i","no waiting for more so update display")
            self.set_display_widget_infos(data)
        elif status["wait_for"] >= status["message"]:
            log("i",f"message n_{status['message']} over a total of {status['wait_for']}")
            infos = self.info_widget.infos
            for k,v in data.items():
                infos[k] = v
            self.set_display_widget_infos(infos)
        self.generate_interface()

    def change_ctx(self,ctx):
        self.context = ctx 
        return self.context

    def keyPressEvent(self, event):

        if event.key == Qt.Key_Escape:
            QApplication.quit()
        
    def quit(self):
        QApplication.quit()


class FullModeApp(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Full Mode App")
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        main_layout = QVBoxLayout(self)

        # ---- MenuBar ----
        self.menu_bar = QMenuBar()
        file_menu = QMenu("File", self)
        edit_menu = QMenu("Edit", self)
        help_menu = QMenu("Help", self)

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

        # Left: sessions & captures tree view with search
        left_layout = QVBoxLayout()
        
        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Filter sessions/captures...")
        self.search_bar.textChanged.connect(self.filter_tree)
        left_layout.addWidget(self.search_bar)

        # Tree
        self.session_tree = QTreeWidget()
        self.session_tree.setHeaderHidden(True)
        self.session_tree.itemDoubleClicked.connect(self.open_analysis)
        left_layout.addWidget(self.session_tree, 1)

        # Example sessions/captures
        self.populate_tree()

        central_layout.addLayout(left_layout, 1)

        # Right: main tab area
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        central_layout.addWidget(self.tab_widget, 3)

        main_layout.addLayout(central_layout)

    def populate_tree(self):
        # Clear tree first
        self.session_tree.clear()

        session1 = QTreeWidgetItem(["Session 1"])
        QTreeWidgetItem(session1, ["Capture A"])
        QTreeWidgetItem(session1, ["Capture B"])

        session2 = QTreeWidgetItem(["Session 2"])
        QTreeWidgetItem(session2, ["Capture X"])
        QTreeWidgetItem(session2, ["Capture Y"])

        self.session_tree.addTopLevelItem(session1)
        self.session_tree.addTopLevelItem(session2)

        self.session_tree.expandAll()

    def filter_tree(self, text):
        text = text.lower()
        for i in range(self.session_tree.topLevelItemCount()):
            session_item = self.session_tree.topLevelItem(i)
            session_visible = False
            for j in range(session_item.childCount()):
                capture_item = session_item.child(j)
                match = text in capture_item.text(0).lower()
                capture_item.setHidden(not match)
                if match:
                    session_visible = True
            session_item.setHidden(not session_visible)

    # ---- Functions ----
    def new_session(self):
        log("i","New session triggered")

    def open_analysis(self, item, column):
        if item.parent() is None:
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

class Context:
    def __init__(self,window,user):
        self.window = window
        self.user = user
        self.session = None
        self.window_name = self.extract_application_from_window_name()

    def extract_application_from_window_name(self):

        my_match = re.search(r'[-—]\s*([^—\-\n]+)\s*$', self.window["name"])
    
        if my_match : 
            log("s",f"match : {my_match.group(1)}")
            res = re.sub(" ","",my_match.group(1))
        #return my_match.group(1)mmmmmmm

        else :
            log("w","not matched the regex")
            res = re.sub(" ","",self.window["name"])
        log("d",res)
        return res
    
    def change_window(self,window):
        self.window = window
        self.window_name = self.extract_application_from_window_name()
    
    #def to_json(self):
    #    return json.dumps(self.__dict__)
    
    def to_json(self):
        serializable = {k: (list(v) if isinstance(v, tuple) else v) for k,v in self.__dict__.items()}
        return json.dumps(serializable)

    

def main(window,user_id="test"):
    # Global task queue
    task_queue = queue.Queue()

    #task_queue.get()

    # Start the worker thread
    threading.Thread(target=worker, daemon=True,args=(task_queue,)).start()
    #db = Database()
    #db.create_tables()
        #if self.context.user == "test":
        #    self.db.add_user(self.context.user)
    #log("d",f"{db.show_tables()}")
    #log("d",f"users  :{db.get_all_items_from_table('users')}")

    context = {"window":window,"user":user_id}
    context = Context(window,user_id)
    #window_name = extract_application_from_window_name(context)
    #context["window_name"] = window_name

    log("d",f"{window}")

    if window:
        log("s",f"Fenêtre active : {window['name']} ({window['size'][0]}x{window['size'][1]})")
        app_qt = QApplication(sys.argv)
        display_dict = context.__dict__.copy()
        overlay = Overlay(text="",x=1400,y=600,context=context,display_dict=display_dict)
        listen_keyboard(overlay,task_queue,context)
        listen_mouse(overlay,task_queue,context)
        overlay.show()
        
        sys.exit(app_qt.exec_())
    else:
        log("c","Impossible d'obtenir la fenêtre active.")

if __name__=="__main__":
    window = get_active_window()
    user_id = connection.main()
    if user_id != None:
        main(window,user_id)
    else :
        main(window)