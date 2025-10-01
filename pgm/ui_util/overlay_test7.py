import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
#from PyQt5.QtGui import QFont
import subprocess
#import requests
import re
from pynput import keyboard,mouse

from datetime import datetime


import imageio.v3 as iio
from PIL import Image

import queue
import threading

import json
import socket
import connection

#import sqlite3
#from loguru import logger v
from pgm.ui_util.log import log,init_log
from pgm.ui_util.db import Database
import pgm.contract as ct

#import time
#import hashlib

from display_widget import DisplayInfo as DI
from full_mode import FullModeApp as FMA
from context import Context as CTX
from capture import Capture as CPT,Sender as SND

init_log()

# to remove once app in prod !
default_user_id = "test"
default_user_mail = "test@test.test"
default_user_pwd = "test"


default_infos = {"title": "my article review","author":"glecomte","numbers":[0,1,2,3],"sub_dict":{"revelance":0,"global_score":0,"sub_list":[2,3,5,7,11]}}
default_infos2 = {"window_name": "default","user":"default"}
controls = {"action":{keyboard.Key.ctrl,keyboard.Key.alt},
            "quit":{keyboard.Key.ctrl,keyboard.Key.esc}}

default_infos3 = {"app":{"tips":{"actions":"to make an action press ctrl+alt then a key in the actions list"},
                         "shortcuts":{"quit":"ctrl+esc","actions":"ctrl+alt+<key>"},
                         "actions":{"single capture":"c","feed capture":"f","video capture":"v","stop video caputre":"s","escape":"e"}},
                "context":{},
                "infos":{}}
handler_addr = "http://localhost:5000/process_image"
handler_portal = "http://localhost:5000/portal"
handler_aggregate = "http://localhost:5000/aggregate"

    
def extract_application_from_window_name(context:CTX):
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
def action_worker(task_queue:queue.Queue):
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

def db_worker(db_queue):
    db = Database()
    db.create_tables()  # called once
    while True:
        func, args,result_q = db_queue.get()
        flag_res = False
        flag = False
        err = None
        res = None
        try:
            log("i",f"executing {func}")
            res = func(db, *args)
            if result_q:
                flag_res = True
                result_q.put(res)
            flag  = True
            log("s",f"ended try block ! flag should be true : {flag}" if flag_res == False else f"ended try block ! flag should be true : {flag} and there is a result !")
        except Exception as e:
            err = e
            if result_q :
                result_q.put(res)
                flag = True
            log("w",f"Error in DB task: {e}" if flag == False else f"Error in DB Task : {e} but get a result :{res}")
        finally:
            db_queue.task_done()
            if flag == False:
                log("w",f"couldn't do the task {db_queue} : {func} : {err}")
            else :
                log("s",f"task {db_queue}: {func} effectued successfully")



def capture_info(first:tuple[int,int],second:tuple[int,int]):
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
    update_capture_state = pyqtSignal()
    update_timer = pyqtSignal(int)
    update_display = pyqtSignal()
    update_capture = pyqtSignal(CPT)
    change_ctx = pyqtSignal(CTX)

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
    def __init__(self,context:CTX,task_queue:queue.Queue,db_queue:queue.Queue, text:str="Overlay HUD", x:int=100, y:int=100, w:int=400, h:int=400,display_dict:dict=None,max_capture:int=10):
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
        
        self.capture_state = False
        
        self.comm = Communicate()
        
        self.comm.update_text.connect(self.set_text2)
        self.comm.update_mod.connect(self.change_mod)
        self.comm.update_infos.connect(self.set_display_widget_infos)
        self.comm.update_capture_state.connect(self.change_capture_state)
        self.comm.update_timer.connect(self.set_timer)
        self.comm.update_capture.connect(self.update_capture)
        self.comm.update_display.connect(self.update_display)
        self.comm.change_ctx.connect(self.change_ctx)

        self.display = True

        self.timer = None
        self.current_capture = None

        self.task_queue = task_queue
        self.db_queue = db_queue

        self.my_sender = None
        self.number_capture = 0
        self.max_capture = max_capture
        self.packet_send = 0


        self.context = context
        
        #self.db = db
        """
        #self.db = Database()
        self.db.create_tables()

        #log("w",f"user : {context.user} ; exist ? : {self.db.get_user(context.user)}")
        self.db.create_default_user()
        log("w",f"user : {context.user} ; exist ? : {self.db.get_user(context.user)}")
        """
        #self.db.add_session(self.context.user)
        #self.db_queue.put((Database.add_session,(self.context.user,),None))
        make_request(self.db_queue,Database.add_session,(self.context.user,))
        #log("d",f"sessions : {self.db.get_all_items_from_table('sessions')}")
        """
        res_q = queue.Queue()
        #self.id_session= self.db.get_session(self.context.user)
        db_queue.put((Database.get_session,(self.context.user,),res_q))
        self.id_session = res_q.get()
        """
        self.id_session = make_request(self.db_queue,Database.get_session,(self.context.user,),True)
 
        if self.id_session == None:
            log("w","default session id loaded (0)")
            self.id_session = 0
        else :
            log("s",f"session id = {self.id_session}")
        self.context.session = self.id_session
        
        
        self.server_thread = SocketServerThread(callback=self.comm.update_infos.emit)
        self.server_thread.start()
       
        self.colors = ["red","blue","green"]
        self.mod = 0
        self.mods= {0:"partial",1:"full"}

        self.create_interface()
        self.generate_interface()
    
    def update_capture(self,capture:CPT):
        self.current_capture = capture
        self.db.add_capture(capture.session,capture.app_id,capture.user)
    
    def update_display(self):
        log("d",f"in update display : {self.display}")
        if self.mods[self.mod] == "partial":
            if self.display:
                self.info_widget3.hide()
            else:
                self.info_widget3.show()
            self.display = not self.display

    def set_timer(self,ms=0):
        self.my_sender = SND(self.context)
        if ms !=0:
            if self.timer == None:
                self.timer = QTimer()
                self.timer.setInterval(ms)
                self.timer.timeout.connect(self.to_trigger)
                self.timer.start()
        else:
            if self.timer != None:
                self.timer.stop()
                self.timer = None
                self.current_capture = None
                self.my_sender = None
                self.number_capture = 0
                self.packet_send = 0
    
    def to_trigger(self):
        flag = False
        self.number_capture += 1
        self.task_queue.put((self.current_capture.capture,()))
        self.my_sender.add_capture(self.number_capture,self.current_capture)
        self.current_capture = CPT(self.current_capture.user,self.current_capture.session,
                                       self.current_capture.window_name,datetime.now(),
                                       self.current_capture.pos,self.current_capture.size,
                                       self.current_capture.context,
                                       save=True)
        
        log("i",f"len sender captures = {len(self.my_sender.captures)}")
        if len(self.my_sender.captures) >= self.max_capture:
            self.task_queue.put((self.my_sender.send_all, ()))
            #vself.my_sender.captures = {}
            self.packet_send += 1

        print("triggering capture")

    def change_capture_state(self,state):

        self.capture_state = state
        

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

        self.fullmode = FMA()
        self.info_widget3 = DI({"analyser":self.display_dict})

    def generate_interface(self):

        mod = self.mods[self.mod]
    
        if mod == "partial" :
            self.setup_partial_mode()
        elif mod == "full":
            self.setup_full_mode()


    def setup_partial_mode(self):

        self.fullmode.hide()
        if self.display:

            self.info_widget3.show()
        

    def setup_full_mode(self):
         # Menu bar
        self.fullmode.activateWindow()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)

        for c in self.fullmode.findChildren(QWidget):
            c.setAttribute(Qt.WA_TransparentForMouseEvents,False)
        self.fullmode.showMaximized()
        self.info_widget3.hide()

    def set_text2(self,my_dict:dict,color=None):

        self.add_dict_to_info(my_dict,"context")

    def set_display_widget_infos(self,infos:dict):
        log("d",f"in infos :{infos}")

        self.add_dict_to_info(infos,"infos")

    def add_dict_to_info(self,my_dict:dict,name:str):
 
        self.display_dict[name] = my_dict
        self.info_widget3.set_infos(self.display_dict)
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



def listen_keyboard(qwidget:Overlay,task_queue:queue.Queue,context:CTX):

    pressed = set()

    def stop_capture_multiple():
        #qwidget.comm.update_capture_state.emit()
        qwidget.comm.update_timer.emit(0)

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
        # tmp comment to test SND/CPT
        #task_queue.put((capture_window,(window_info,context)))
        cap = CPT(context.user,context.session,context.window_name,datetime.now(),window_info["pos"],window_info["size"],context)
        sender = SND(context)
        # may take sender as attribute ? so instead of add capture , once in cap.capture it add capture automatically at the end (avoid potential conflict in the queue (calling sender with unexisting capture ?))
        task_queue.put((cap.capture,("args to test","arg2 to test")))
        #cap.add_to_sender(sender)
        sender.add_capture(cap.idc,cap)
        log("d",f"sender captures {sender.captures}")
        task_queue.put((sender.send_all,("arg1","arg2")))

    def capture_multiple():
        first,second = wait_for_two_clicks()
        log("s",f"first : {first} ; second : {second}")
        window_info = capture_info(first,second)
        log("s",f"window info {window_info}")
        # should call an action in the queue

        cap = CPT(context.user,context.session,context.window_name,datetime.now(),window_info["pos"],window_info["size"],context)

        qwidget.comm.update_capture.emit(cap)
        qwidget.comm.update_timer.emit(100)

    def capture_feed():
        first,second = wait_for_two_clicks()
        window_info = capture_info(first,second)
        sender = SND(context,addr=handler_aggregate)
        cap = CPT(context.user,context.session,context.window_name,datetime.now(),window_info["pos"],window_info["size"],context)

        print("capture 0")
        nb_cap = 0
        sender.add_capture(nb_cap,cap)
        def on_scroll(x,y,dx,dy,injected=False):
            nonlocal nb_cap,cap
            if dy > 0: 
                sender.send_all()
                return False
            else :
                nb_cap +=1
                print(f"capture {nb_cap}")
                last_cap = cap
                cap = CPT(context.user,context.session,context.window_name,datetime.now(),window_info["pos"],window_info["size"],context)
                if cap.im_hash != last_cap.im_hash:
                    sender.add_capture(nb_cap,cap)
                else :
                    cap.remove_capture()

        listener_mouse = mouse.Listener(on_scroll=on_scroll)
        listener_mouse.start()
        # f
        
    def escape():
        print("in escape ")
        qwidget.comm.update_display.emit()


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
            # capture_multiple and stop_capture may trigger wait_capture ?v
            log("d",f"action {action_key} should be triggered")
            if action_key == keyboard.KeyCode.from_char("c"):
                capture()
            elif action_key == keyboard.KeyCode.from_char("m"):
                change_mod()
            elif action_key == keyboard.KeyCode.from_char("v"):
                capture_multiple()
            elif action_key == keyboard.KeyCode.from_char("s"):
                stop_capture_multiple()
            elif action_key == keyboard.KeyCode.from_char("f"):
                capture_feed()
            elif action_key == keyboard.KeyCode.from_char("e"):
                escape()
        pressed.discard(key)
        return context

    def event(e):
        to_print = {"last event":e}
        qwidget.comm.update_text.emit(to_print)
        ctx = event_appened(context,qwidget)
        qwidget.change_ctx(ctx)




    listener = keyboard.Listener(on_press=on_press,on_release=on_release)
    listener.start()

def listen_mouse(qwidget:Overlay,task_queue:queue.Queue,context:CTX):
    
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
       
def event_appened(context:CTX,qwidget:Overlay=None,to_print:bool=False):
    current = get_active_window()
    if current != None:
        if current != context.window:
            log("i",f"window changed from : {context.window}\nto :{current}")
            context.change_window(current)
  
            window_name = context.window_name
            #app_id = db.get_app(app_name=window_name)
            app = make_request(qwidget.db_queue,Database.get_app,(None,window_name),True)
            log("i",f"app : {app}")
            if app == None:
                log("i",f"app = None => adding app into db")
                make_request(qwidget.db_queue,Database.add_app,(window_name,))
                app = make_request(qwidget.db_queue,Database.get_app,(None,window_name),True)
                log("i",f"app created : app = {app}") if app != None else log("w","an error occured app = None !")

            app_id = app[0]
            log("s",f"app id = {app_id}")
            context.app_id = app_id
            #context.app_id = app_id

            to_display = {"window name : ":window_name}
            qwidget.comm.update_text.emit(to_display)
            qwidget.change_ctx(context)

    return context

def make_request(db_queue:queue.Queue,db_func:callable,func_arg:tuple=(),need_result:bool=False,timeout:float=1):
    log("d",f"making a request : {db_func} with args : {func_arg} and awaiting for a result : {need_result} for {timeout} s")
    res = None
    if need_result:
        res_q = queue.Queue()
        db_queue.put((db_func,func_arg,res_q))
        try :
            res = res_q.get(timeout=timeout)
            log("s",f"request succeded and result is : {res}")
        except queue.Empty:
            log("w",f"request timeout no answer")
            res = None
    else :
        db_queue.put((db_func,func_arg,None))
        log("s",f"succeeding and not waiting for answer")

    return res

def main(window:dict[str,any],user_id:str=default_user_id):
    # Global task queue
    task_queue = queue.Queue()

    # Start the worker thread
    threading.Thread(target=action_worker, daemon=True,args=(task_queue,)).start()

    db_queue = queue.Queue()

    threading.Thread(target=db_worker, daemon=True, args=(db_queue,)).start()

    if user_id == default_user_id:
        db_queue.put((Database.create_default_user,(default_user_id,default_user_mail,default_user_pwd),None))

    context = {"window":window,"user":user_id}
    context = CTX(window,user_id)

    log("d",f"{window}")

    if window:
        log("s",f"Fenêtre active : {window['name']} ({window['size'][0]}x{window['size'][1]})")
        app_qt = QApplication(sys.argv)
        #display_dict = context.__dict__.copy()

        overlay = Overlay(task_queue=task_queue,text="",x=1400,y=600,context=context,display_dict=default_infos3,db_queue=db_queue)
        listen_keyboard(overlay,task_queue,context)
        #listen_mouse(overlay,task_queue,context)
        overlay.show()
        
        sys.exit(app_qt.exec_())
    else:
        log("c","Impossible d'obtenir la fenêtre active.")



if __name__=="__main__":
    window = get_active_window()
    #print(window)
    user_id = connection.main()
    #db = Database()
    #db.create_tables()
    
    #if user_id == None:
    #    db.create_default_user(default_user_id,default_user_mail,default_user_pwd)
    #db_queue = queue.Queue()

    #threading.Thread(target=db_worker, daemon=True, args=(db_queue,)).start()

    log("i",f"user = {user_id}"  if user_id != default_user_id else f"default user :{user_id}")
    if user_id !=None:
        main(window,user_id)
    else : 
        main(window)