import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QFont
import threading
import socket
import subprocess
from pynput import keyboard,mouse


import subprocess
import mss
import os
from datetime import datetime

# la boucle est mal faire dans ctrl (peut causer core dump!!)

#import threading
import time
#import numpy as np
#from cv2 import imencode
import requests

import imageio.v3 as iio
import io
from PIL import Image

actions = {"capture":keyboard.Key.ctrl,"change_mod":keyboard.Key.alt}

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


def ctrl_event(qwidget,context):
    print("in control event")
    
    #listener2.stop()
    first_click_coord = None
    second_click_coord = None
    #listener1 = mouse.Listener(on_click=on_click1)
    #listener1.start()

    # here a segfault if no move before click
    with mouse.Events() as e:
        """
        event = e.get()
        if event is None:
            print("didn't click at all closing ctrl mode")
        elif type(event) == mouse.Events.Click:
            print(event)
        else :
            #print("not a click !")
            while type(event) != mouse.Events.Click:
                event = e.get()
        """
        event = None
        while type(event) != mouse.Events.Click:
                event = e.get()
        
        #print(type(event))
        first_click_coord = event.x,event.y
        #print(first_click_coord)
    print("first click achieved")
    time.sleep(0.1)

    with mouse.Events() as e:
        """
        event2 = e.get()
        if event2 is None:
            print("didn't click at all closing ctrl mode")
        elif type(event2) == mouse.Events.Click:
            print(event2)
        else :
            #print("not a click !")
            while type(event2) != mouse.Events.Click:
                event2 = e.get()

        #print(type(event2))
        second_click_coord = event2.x,event2.y
        #print(second_click_coord)
        """
        event = None
        while type(event) != mouse.Events.Click:
                event = e.get()
        second_click_coord = event.x,event.y
        print("second click achieved")
    pos = first_click_coord[0] if first_click_coord[0]<second_click_coord[0] else second_click_coord[0],first_click_coord[1] if first_click_coord[1]<second_click_coord[1] else second_click_coord[1]
    print(pos)
    size = abs(first_click_coord[0]-second_click_coord[0]),abs(first_click_coord[1]-second_click_coord[1])
    print(size)
    window_info = {"pos":pos,"size":size}

    capture_window(window_info)
    #print(context["window"])
    print("closing ctrl event")


def listen_keyboard(qwidget,context):
    #print("press esc to escape overlay ! =) ")

    def change_mod():
        #print("<ctrl>+<alt> pressed")
        qwidget.comm.update_mod.emit()

    def leave_app():
        qwidget.quit()
    
    def capture():
        print("capture pressed")
        ctrl_event(qwidget,context)
    
    def on_press(key):
        print(key)
        flag_multiple_pressed = False

        with keyboard.GlobalHotKeys({"<ctrl>+<alt>":change_mod,
                                     "<ctrl>+<esc>":leave_app,
                                     "<ctrl>+<alt>+c":capture}) as h:
            h.join()
        """
        if key == keyboard.Key.esc:
            print("ESC pressé, on quitte !")
            #sys.exit(0)  # stoppe tout le script
            #qwidget.keyPressEvent(key)
            qwidget.quit()
        elif key == keyboard.Key.ctrl:
            #filename = capture_window(context["window"])
            #print(f"ctrl was hit, {filename} saved")
            ctrl_event(qwidget,context)
            print(key)
        elif key == keyboard.Key.alt:
            #qwidget.change_mod()
            qwidget.comm.update_mod.emit()
        else :
            print(f"{key}")
            
        event(f"key_pressed {key}")
        """

    def event(e):
        qwidget.comm.update_text.emit(e)
        #ctx = event_appened(context,True)
        #qwidget.change_ctx(ctx)

    listener = keyboard.Listener(on_press=on_press)
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
    update_text = pyqtSignal(str)
    update_mod = pyqtSignal()

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
                        print("recived from handler : ",data)
                        if self.callback:
                            self.callback(data.decode())


class Overlay(QWidget):
    def __init__(self, text="Overlay HUD", x=100, y=100, w=400, h=400,context=None):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)  # Click-through
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.pos = (x,y,w,h)
        self.text = text
        #self.set_text()
        self.comm = Communicate()
        self.comm.update_text.connect(self.set_text)
        self.comm.update_mod.connect(self.change_mod)
         
        self.setGeometry(self.pos[0], self.pos[1], self.pos[2], self.pos[3])
        self.label = QLabel(self.text, self)
        self.label.setFont(QFont("Arial", 20))
        self.label.setStyleSheet("color: red; background-color: rgba(0,0,0,100);")
        self.label.setAlignment(Qt.AlignCenter)
        if context == None:
            self.context = {}
        else :
            self.context = context
        
        
        self.server_thread = SocketServerThread(callback=self.comm.update_text.emit   )
        self.server_thread.start()
        self.mod = 0
        self.colors = ["red","blue","green"]
    def change_mod(self):
        #print("mode : ",self.mod)
        self.mod = (self.mod+1) % len(self.colors)
        self.generate_interface()
        #print("mode : ",self.mod)

    def generate_interface(self):
        print("generating interface ")
        
        """
        if self.mod == 0:
            color = "red"
        elif self.mod == 1:
            color = "blue"
        elif self.mod == 2:
            color = "green"
        else :
            color = "white"
        """
        color = self.colors[self.mod]
        self.label.deleteLater()
        #self.setGeometry(self.pos[0], self.pos[1], self.pos[2], self.pos[3])
        self.label = QLabel(self.text, self)
        self.label.setFont(QFont("Arial", 20))
        self.label.setStyleSheet(f"color: {color}; background-color: rgba(0,0,0,100);")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.show()

    def set_text(self,text=""):
        
        if text == "":
            text = self.text
        #print(f"updating {text}")
        self.label.setText(text)
        #print(text)
        
        #self.label.repaint()
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
    