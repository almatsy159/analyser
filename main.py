import subprocess
import mss
import os
from datetime import datetime


import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QFont

from pynput import keyboard
from pynput import mouse

# allow execution of opencv without conflict with pygt overlay (cause opencv work with pyqt apparently) but cause the overlay to not be activated ...*
# look for qthread to solve this

#os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "0"
#os.environ["QT_QPA_PLATFORM"] = "offscreen"

#import cv2
#import pytesseract
#import numpy as np

#import threading
import re

def get_filename_only(path):

    # Regex to capture filename without extension
    match = re.search(r'/([^/]+)\.[^/.]+$', path)

    if match:
        filename_without_ext = match.group(1)
        print(filename_without_ext)
    return filename_without_ext


"""
def process_screenshot(path,container):
    print(f"processing screenshot {path}")
    img = cv2.imread(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Amélioration du contraste + Binarisation
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY_INV, 11, 2)

    # Détection des contours (blocs de texte)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    blocks = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 50 and h > 20:  # Filtre les petits bruits
            roi = img[y:y+h, x:x+w]
            text = pytesseract.image_to_string(roi, lang='eng+fra')
            if text.strip():
                blocks.append({"coords": (x, y, w, h), "text": text.strip()})
                cv2.rectangle(img, (x, y), (x+w, y+h), (0,255,0), 2)

    print(path)
    path_to_write_cv2_img = get_filename_only(path)
    cv2.imwrite(f"data/cv2/{path_to_write_cv2_img}.png", img)
    container["blocks"]= blocks
    #return blocks

"""
"""
blocks = process_screenshot("data/screenshot.png")
for b in blocks:
    print(b)
"""


# press esc to escape overlay ! =) 
class Communicate(QObject):
    update_text = pyqtSignal(str)

def event_appened(context,to_print=False,qwidget=None):
    current = get_active_window()
    if to_print:
        print(f"first context : {context}")
        print(current)
    if current != context["window"]:
        print("window changed")
        context["window"]= current
        if qwidget != None:
            qwidget.quit()
        filename =capture_window(current)
        """
        blocks = {}

        thread = threading.Thread(target=process_screenshot,args=(filename,blocks))
        thread.start()
        thread.join()
        
        path_to_create_txt = get_filename_only(filename)
        with open(f"data/txt/{path_to_create_txt}.txt","w") as f:
            for b in blocks["blocks"]:
                f.write(f"{b}\n²")
            #f.write(blocks)
        #for b in blocks["blocks"]:
            #print(b)
        """



    return context
            

def listen_keyboard(qwidget,context):
    #print("press esc to escape overlay ! =) ")
    def on_press(key):

        if key == keyboard.Key.esc:
            print("ESC pressé, on quitte !")
            #sys.exit(0)  # stoppe tout le script
            #qwidget.keyPressEvent(key)
            qwidget.quit()
        elif key == keyboard.Key.ctrl:
            filename = capture_window(context["window"])
            print(f"ctrl was hit, {filename} saved")
        else :
            print(f"{key}")
        event(f"key_pressed {key}")

    def event(e):
        qwidget.comm.update_text.emit(e)
        ctx = event_appened(context,True)
        qwidget.change_ctx(ctx)

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
        ctx = event_appened(context)
        qwidget.change_ctx(ctx)
    # ...or, in a non-blocking fashion:
    listener = mouse.Listener(
        on_move=on_move,
        on_click=on_click,
        on_scroll=on_scroll)
    listener.start()

class Overlay(QWidget):
    def __init__(self, text="Overlay HUD", x=100, y=100, w=800, h=100,context=None):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)  # Click-through
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.pos = (x,y,w,h)
        self.text = text
        #self.set_text()
        self.comm = Communicate()
        self.comm.update_text.connect(self.set_text)
        self.setGeometry(self.pos[0], self.pos[1], self.pos[2], self.pos[3])
        self.label = QLabel(self.text, self)
        self.label.setFont(QFont("Arial", 20))
        self.label.setStyleSheet("color: red; background-color: rgba(0,0,0,100);")
        self.label.setAlignment(Qt.AlignCenter)
        if context == None:
            self.context = {}
        else :
            self.context = context

    def set_text(self,text=None):
        
        if text == None:
            text = self.text
        #print(f"updating {text}")
        self.label.setText(text)
        
        #self.label.repaint()
    def change_ctx(self,ctx):
        self.context = ctx

    def keyPressEvent(self, event):

        if event.key == Qt.Key_Escape:
            QApplication.quit()  # ferme l'application
        
    def quit(self):
        QApplication.quit()



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


def capture_window(window_info, save_dir="data/img"):
    """Capture la fenêtre active et enregistre l'image."""
    if not window_info:
        print("Aucune fenêtre active détectée.")
        return

    x, y = window_info["pos"]
    w, h = window_info["size"]

    os.makedirs(save_dir, exist_ok=True)
    filename = os.path.join(save_dir, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")

    with mss.mss() as sct:
        sct_img = sct.grab({"top": y, "left": x, "width": w, "height": h})
        mss.tools.to_png(sct_img.rgb, sct_img.size, output=filename)

    print(f"Capture enregistrée : {filename}")

    return filename




if __name__ == "__main__":
    # get context 
    window = get_active_window()
    context = {"window":window}
    #print(window)

    if window:
        print(f"Fenêtre active : {window['name']} ({window['size'][0]}x{window['size'][1]})")
        file = capture_window(window)
        
        app = QApplication(sys.argv)
        overlay = Overlay(text=f"{context['window']['name']}", x=500, y=300,context=context)
        listen_keyboard(overlay,context)
        listen_mouse(overlay,context)
        overlay.show()

        # check if the overlay doesn't got the focus ! (apperently not !)
        #print(get_active_window())
        
        sys.exit(app.exec_())
    else:
        print("Impossible d'obtenir la fenêtre active.")
