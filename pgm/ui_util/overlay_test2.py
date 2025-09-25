import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget,QVBoxLayout,QHBoxLayout,QSizePolicy
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QFont
import threading
import socket
import subprocess
from pynput import keyboard,mouse


import mss
import os
from datetime import datetime

# la boucle est mal faire dans ctrl (peut causer core dump!!)

#import threading
import time
#import numpy as npc
#from cv2 import imencode
import requests
import json

import imageio.v3 as iio
import io
from PIL import Image

"""
controls = {"mode":{keyboard.Key.ctrl_r,keyboard.Key.alt,keyboard.KeyCode.from_char('m')},
            "capture":{keyboard.Key.ctrl_r,keyboard.Key.alt,keyboard.KeyCode.from_char('c')},
            "quit":{keyboard.Key.ctrl_r,keyboard.Key.esc}}
"""
controls = {"action":{keyboard.Key.ctrl,keyboard.Key.alt},
            "quit":{keyboard.Key.ctrl,keyboard.Key.esc}}
# actions should be tied to function directly ? or should generate a json with function ? or not editable for this part ?(right now it's that one)
actions = {"c":"capture","m":"change_mod"}

default_infos = {"title": "my article review","author":"glecomte","numbers":[0,1,2,3],"sub_dict":{"revelance":0,"global_score":0,"sub_list":[2,3,5,7,11]}}


handler_addr = "http://localhost:5000/process_image"

def capture_window(window_info, save_dir="data/img"):

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

    print("executing capture")
    if w ==0 or h ==0:
        print("can't caputre no width or height frame =x")
    else :
        with mss.mss() as sct:
            sct_img = sct.grab({"top": y, "left": x, "width": w, "height": h})
            #img = np.array(sct_img)[:,:, :3].astype(np.uint8)
            img = Image.frombytes("RGB",sct_img.size,sct_img.rgb)
            mss.tools.to_png(sct_img.rgb, sct_img.size, output=filename)

        print(f"Capture enregistrée : {filename}")

        # here need to convert img to send it to the handler !

        # send image to handler
    
    
        # temporary 
        #img = "image not encoded in overlay.py:capture window yet."
        #_,img_encoded = imencode(".png",img)
        #files = {"image":{"screenshot.png",img_encoded.tobytes(),"image/png"}}
        buf = io.BytesIO()
        iio.imwrite(buf, img, format='PNG')
        buf.seek(0)
        #print(filename_tmp)
        files = {"image":(filename,buf,"image/png")}
        try :
            response = requests.post(handler_addr,files=files)
        except :
            response = None
        finally :
            if response == None:
                print("connection could be achieved : capture not")
            else:
                print("handler response:",response)
        #print("handler response : ",response.json())

    return filename,save_dir

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




def listen_keyboard(qwidget,context=None):
    if context == None:
        context = {}
    #print("press esc to escape overlay ! =) ")
    pressed = set()

    def change_mod():
        #print("<ctrl>+<alt> pressed")
        qwidget.comm.update_mod.emit()

    def capture():
        print("in capture")
        first,second = wait_for_two_clicks()
        print(first)
        print(second)
        window_info = capture_info(first,second)
        capture_window(window_info)
       

    def leave_app():
        qwidget.quit()

    def on_press(key):
        print(f"{key} pressed !")
        pressed.add(key)

    def on_release(key):
        print(pressed)
        action_key = None
        
        if controls["quit"] == pressed:
            print("escaping the app")
            leave_app()
        elif controls["action"] == pressed:
            print("wait for action launched !")
            action_key = wait_for_action()
        """
        elif controls["capture"] == pressed:
            capture()
        elif controls["mode"] == pressed:
            change_mod()
        """
        if action_key:
            print(f"action {action_key} should be triggered")
            if action_key == keyboard.KeyCode.from_char("c"):
                capture()
            elif action_key == keyboard.KeyCode.from_char("m"):
                change_mod()
        pressed.discard(key)
        print(pressed)




    listener = keyboard.Listener(on_press=on_press,on_release=on_release)
    listener.start()

def listen_mouse(qwidget,context):
    
    def on_move(x, y, injected):

        #print(f"Pointer mover to {x},{y},it was {'faked' if injected else 'not faked'}")
        event("on_move")

    def on_click(x, y, button, pressed, injected):

        #print(f"{pressed} at {x},{y} with {button} ,it was {'faked' if injected else 'not faked'}")
        """
        if not pressed:
        # Stop listener
            return False
        """
        event("on click")

    def on_scroll(x, y, dx, dy, injected):
       
        #print(f"Scrolled {'down' if dy<0 else 'up'} at {x},{y} for {dx},{dy} and it was {'faked' if injected else 'not faked'}")
        event("on_scroll")

    def event(e):
        #qwidget.text = e
        qwidget.comm.update_text.emit(e)
        #ctx = event_appened(context)
        #qwidget.change_ctx(ctx)
    # ...or, in a non-blocking fashion:
    listener = mouse.Listener(
        on_move=on_move,
        on_click=on_click,
        on_scroll=on_scroll)
    listener.start()



class Communicate(QObject):
    update_text = pyqtSignal(str)
    update_mod = pyqtSignal()
    update_infos = pyqtSignal(dict)


class DisplayInfo(QWidget):
    def __init__(self,infos=None,parent=None):
        """
        super().__init__()
        
        self.setLayout(QVBoxLayout())
        """
        super().__init__(parent)
        
        self.setGeometry(500,500,500,500)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents,True)
        
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
        #self.show()

    """def generate_view(self):
        for k,v in self.infos.items():
            h_layout = QHBoxLayout()
            k_label = QLabel(f"{k}")
            v_label = QLabel(f"{v}")
            h_layout.addWidget(k_label)
            h_layout.addWidget(v_label)
            self.layout.addWidget(h_layout)"""

    def create_info_widget(self, my_dict=None,previous_layout=None):
        print(my_dict)
        if my_dict is None:
            my_dict = {}

        # Container for all lines
        container_widget = QWidget()
        container_widget.setAttribute(Qt.WA_TransparentForMouseEvents,True)
        container_layout = QVBoxLayout(container_widget)
        container_layout.setSpacing(5)

        for k, v in my_dict.items():
            # Layout for this line
            line_layout = QHBoxLayout()
            line_layout.setSpacing(10)
            

            # Key label
            key_label = QLabel(str(k))
            key_label.setAttribute(Qt.WA_TransparentForMouseEvents)
            key_font = QFont("Segoe UI", 10, QFont.Bold)
            key_label.setFont(key_font)
            key_label.setStyleSheet("color: #00aaff;")
            key_label.adjustSize()
            line_layout.addWidget(key_label)

            # Value or nested dict
            if isinstance(v, dict):
                print(v)
                #value_widget = QWidget()
                #value_layout = QVBoxLayout()
                #value_layout.setContentsMargins(0, 0, 0, 0)
                #value_layout.setSpacing(2)
        
                # Recursively create sub-widgets for the nested dict
                sub_widget = self.create_info_widget(v)
                #sub_widget.adjustSize()
                #sub_widget.setMinimumSize(100,100)
                #sub_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                #value_widget.setLayout(value_layout)
                #value_layout.addWidget(sub_widget)
                #sub_widget = self.create_info_widget(v)
                #line_layout.addWidget(value_widget)
                
                line_layout.addWidget(sub_widget)
            else:
                value_label = QLabel(str(v))
                value_label.setAttribute(Qt.WA_TransparentForMouseEvents)
                value_font = QFont("Consolas", 10)
                value_label.setFont(value_font)
                value_label.setStyleSheet("color: white;")
                value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                line_layout.addWidget(value_label)

            line_layout.addStretch()

            # Line container widget
            line_widget = QWidget()
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






    
    def generate_view(self, info_dict=None):
        if info_dict == None:
            info_dict = self.infos
        # Clear previous widgets
        while self.main_layout.count():
            child = self.main_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        
        #for key, value in info_dict.items():
        #    line_layout = QHBoxLayout()
        #    line_layout.setSpacing(10)    
        #    key_label = QLabel(key)
        #    key_font = QFont("Segoe UI", 10, QFont.Bold)
        #    key_label.setFont(key_font)
        #    key_label.setStyleSheet("color: #00aaff;")
            
        #    value_label = QLabel(str(value))
        #    value_font = QFont("Consolas", 10)
        #    value_label.setFont(value_font)
        #    value_label.setStyleSheet("color: white;")
        #    value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            
        #    line_layout.addWidget(key_label)
        #    line_layout.addWidget(value_label)
        #    line_layout.addStretch()
            
            # Container widget for background & rounded corners
        #    line_widget = QWidget()
        #    line_widget.setLayout(line_layout)
            #line_widget.setStyleSheet("""
            #    background-color: rgba(0, 0, 100, 150);
            #    border-radius: 6px;
            #""")
            
        #    self.main_layout.addWidget(line_widget)
        #    """
        info_widget = self.create_info_widget(info_dict)
        self.main_layout.addWidget(info_widget)
        self.adjustSize()
        self.show()

    def set_infos(self,infos=None):
        self.infos = infos
        self.generate_view()


class SocketServerThread(threading.Thread):
    def __init__(self, host='0.0.0.0', port=5002, callback=None):
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
                            # data should be formated this way in handler {"from_server":{"message":x,"wait_for":y},"result":{json}
                            self.callback(data)
                            
                        

class Overlay(QWidget):
    def __init__(self, text="Overlay HUD", x=100, y=100, w=400, h=400,context=None):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        screen = QApplication.primaryScreen()
        size = screen.size()
        self.w = size.width()
        self.h = size.height()
        self.setAttribute(Qt.WA_TransparentForMouseEvents,True)  # Click-through
        self.setAttribute(Qt.WA_TranslucentBackground)
        #self.pos = (x,y,w,h)
        self.text = text
        #self.set_text()
        self.comm = Communicate()
        self.comm.update_text.connect(self.set_text)
        self.comm.update_mod.connect(self.change_mod)
        #self.comm.update_infos.connect(self.parse_display_widget_infos)
        self.comm.update_infos.connect(self.set_display_widget_infos)
        #self.setGeometry(0,0,self.w,self.h)
        #self.setGeometry(self.pos[0], self.pos[1], self.pos[2], self.pos[3])
        #self.showFullScreen()
    
        self.label = QLabel(self.text, self)
        self.label.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.label.setFont(QFont("Arial", 20))
        self.label.setStyleSheet("color: red; background-color: rgba(0,0,0,100);")
        self.label.setAlignment(Qt.AlignCenter)

        if context == None:
            self.context = {}
        else :
            self.context = context
        
        
        self.server_thread = SocketServerThread(callback=self.comm.update_infos.emit)
        self.server_thread.start()
        self.mod = 0
        self.colors = ["red","blue","green"]
        self.info_widget = DisplayInfo(default_infos,self)

        self.generate_interface()
        
    def change_mod(self):
        #print("mode : ",self.mod)
        self.mod = (self.mod+1) % len(self.colors)
        self.generate_interface()
        #print("mode : ",self.mod)

    def generate_interface(self):
        print("generating interface ")
        
        color = self.colors[self.mod]
        self.label.deleteLater()
    
        #self.setGeometry(self.pos[0], self.pos[1], self.pos[2], self.pos[3])
        self.label = QLabel(self.text, self)
        self.label.setFont(QFont("Arial", 20))
        self.label.setStyleSheet(f"color: {color}; background-color: rgba(0,0,0,100);")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.show()
        
        if self.mod == 0:
            self.info_widget.show()
            self.info_widget.move(100, 500)        # position inside overlay
            self.info_widget.adjustSize() 
            #self.info_widget.resize()
            self.info_widget.show()
        else :
            self.info_widget.hide()
        """
        elif self.mod == 1:
            self.label2 = QLabel("hi im label 2", self)
            self.label2.setFont(QFont("Arial", 20))
            self.label2.setStyleSheet(f"color: orange; background-color: rgba(0,0,0,100);")
            self.label2.move(500,500)
            self.label2.resize(200,200)
            self.label2.setAlignment(Qt.AlignCenter)
            self.label2.show()
        elif self.mod == 2:
            self.label3 = QLabel("hi im label 3", self)
            self.label3.setFont(QFont("Arial", 20))
            self.label3.move(800,800)
            self.label3.resize(200,200)
            self.label3.setStyleSheet(f"color: purple; background-color: rgba(0,0,0,100);")
            self.label3.setAlignment(Qt.AlignCenter)
            self.label3.show()
        """

    def set_text(self,text=""):
        
        if text == "":
            text = self.text
        #print(f"updating {text}")
        self.label.setText(text)
        #print(text)
        
        #self.label.repaint()

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

    def change_ctx(self,ctx):
        self.context = ctx

    def keyPressEvent(self, event):

        if event.key == Qt.Key_Escape:
            QApplication.quit()  # ferme l'application
        
    def quit(self):
        QApplication.quit()


def main():
    window = get_active_window()
    context = {"window":window}
    #print(window)

    if window:
        print(f"Fenêtre active : {window['name']} ({window['size'][0]}x{window['size'][1]})")
        #file = capture_window(window)
        
        app_qt = QApplication(sys.argv)
        overlay = Overlay(text=f"{context['window']['name']}", x=1400, y=600,context=context)
        listen_keyboard(overlay,context)
        listen_mouse(overlay,context)
        overlay.show()

        # check if the overlay doesn't got the focus ! (apperently not !)
        #print(get_active_window())
        
        sys.exit(app_qt.exec_())
    else:
        print("Impossible d'obtenir la fenêtre active.")

if __name__=="__main__":
    main()