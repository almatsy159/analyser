from log import log
import os
import mss
import requests
import hashlib
from PIL import Image
import io
import imageio.v3 as iio

handler_addr = "http://localhost:5000/process_image"
handler_portal = "http://localhost:5000/portal"
handler_aggregate = "http://localhost:5000/aggregate"

class Capture:
    def __init__(self,user,session,window_name,timestamp,pos,size,context,app_id=0,ext="png",save=True,f_dir="data/img"):
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
        self.app_id = app_id

        self.save = save
        
        self.capture()
        self.im_byte = self.img.tobytes()
        self.im_hash = hashlib.md5(self.im_byte).hexdigest()

    def capture(self,a1=None,a2=None,*args):
        with mss.mss() as sct:
            self.sct_img = sct.grab({"top":self.y,"left":self.x,"width":self.w,"height":self.h})
            self.img = Image.frombytes("RGB",self.sct_img.size,self.sct_img.rgb)
            if self.save :
                mss.tools.to_png(self.sct_img.rgb, self.sct_img.size, output=self.f_path)
            
            #self.context.db.add_capture()
    
    def set_id(self,idc=0):
        self.idc = idc

    def write_into_db(self,db):
        # to edit both here and db ...
        #self.context.db.add_capture(self.session,self.app)
        self.idc = self.context.db.get_capture()
    
    def add_to_sender(self,sender):
        sender.add_capture(self.idc,self.app_id)
    
    def remove_capture(self):
        os.remove(self.f_path)
          

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
        log("d",f"in send capture , to send {cid}")

        buf = io.BytesIO()
        iio.imwrite(buf, capture.img, format='PNG')
        buf.seek(0)
        files = {"image":(capture.f_path,buf,f"image/{capture.ext}")}
        data = {"context":self.context.to_json(),"process":self.process,"sid":[self.sender_id,self.sender_id2],"cid":cid}
        
        # validate data following contract constraint 
        #ct.ui_to_handler_data(data)
        flag = False
        try :
            print(f"sending capture {cid}")
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
            print(f"in sendall , should send capture {cid}")
            cpt +=1
            self.send_capture(c,cid)
        self.captures = {}
            #print(res)
            #total[res] +=1
        #print(total)
        #return total


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
