from pgm.ui_util.log import log
import os
import mss
import requests
import hashlib
from PIL import Image
import io
import imageio.v3 as iio
import numpy as np
from skimage.registration import phase_cross_correlation


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
        
        #self.capture()
        #self.im_byte = self.img.tobytes()
        #self.im_hash = hashlib.md5(self.im_byte).hexdigest()
        self.im_byte = None
        self.im_hash = None

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
    
    def compare(self):
        self.im_byte = self.img.tobytes()
        self.im_hash = hashlib.md5(self.im_byte).hexdigest()
          

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

class SenderFeed(Sender):
    def __init__(self, context, process="default", addr=handler_portal):
        super().__init__(context, process, addr)
        self.base_cap = None
        self.base_cap_id = None

    
    def add_capture(self, id_capture, capture):
        if self.captures == {}:
            self.base_cap= capture
            self.base_cap_id = id_capture
            self.captures[id_capture]=capture
        else :
            bcap = self.base_cap
            img,img_size = process_feed(self.base_cap,capture)
            self.base_cap = Capture(bcap.user,bcap.session,bcap.window_name,bcap.timestamp,bcap.pos,img_size,bcap.context,bcap.app_id,bcap.ext,bcap.save,bcap.dir)
            self.base_cap.img = img
        
            #path = bcap.dir + str(self.base_cap_id) + bcap.ext
            self.base_cap.img.save(self.base_cap.f_path)
            self.captures[self.base_cap_id] = self.base_cap
            #capture.remove_capture()
    


""" 

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

"""

def compare_image_scroll_y(arr1,arr2):

    i=0
    idx = 0
    eof = False

    k=0
    print(arr1.shape[0])
    while eof == False:

        for j in range(i,arr1.shape[0]):
            if i == 0 and j==0:
                print(f"L1[{j}] : {arr1[j,:,:]} ==  {arr2[k,:,:]} : L2[{k}]" if np.all(arr1[j,:,:] == arr2[k,:,:]) else f"L1[{j}] : {arr1[j,:,:]} !=  {arr2[k,:,:]} : L2[{k}]")
            if np.all(arr1[j,:,:] == arr2[k,:,:]):
                k=k+1
            else :
                i = i+1
                k=0
                break
        else :
            idx = i
            eof = True

    return idx


#compare_image_scroll_y(img_dict["s11.png"]["img_arr"],img_dict["s12.png"]["img_arr"])

def delta_y_between_images(arr1, arr2):
    """
    Compute vertical shift (delta Y) between two images of same shape.
    Returns the delta Y such that shifting arr2 by deltaY matches arr1 best.

    There is a huge issue here , the maximum number of rows matching isn't necessarely the good offset . It's consecutive rows that work best .
    The while fonction should be better but need apply the good test !
    """
    H1, W, C = arr1.shape
    H2,_,_ = arr2.shape
    H = min(H1,H2)
    max_match = 0
    best_dy = 0

    # Try all possible shifts
    for dy in range(-H + 1, H):
        if dy >= 0:
            # arr2 shifted down
            overlap_arr1 = arr1[dy:H]
            overlap_arr2 = arr2[0:H-dy]
        else:
            # arr2 shifted up
            overlap_arr1 = arr1[0:H+dy]
            overlap_arr2 = arr2[-dy:H]

        # Count number of fully matching rows
        match_count = np.sum(np.all(overlap_arr1 == overlap_arr2, axis=(1,2)))

        if match_count > max_match:
            max_match = match_count
            best_dy = dy

    return best_dy

"""
dy = delta_y_between_images(img_dict["s11.png"]["img_arr"], 
                            img_dict["s12.png"]["img_arr"])
print("Vertical offset (delta Y):", dy)
"""

def merge_images_simple(arr1, arr2, delta_y):
    if delta_y<=0:
        return arr1
    H1, W, C = arr1.shape
    H2, _, _ = arr2.shape

    # Height of the new merged array
    new_H = H1 + (H2 - delta_y)
    #new_H = H1 + delta_y
    merged = np.zeros((new_H, W, C), dtype=arr1.dtype)

    # Put first image at the top
    merged[0:H1-delta_y, :, :] = arr1[0:H1-delta_y]

    # Put the non-overlapping part of the second image
    #merged[H1:H1 + (H2 - delta_y), :, :] = arr2[delta_y:, :, :]
    #merged[H1:H1 + delta_y, :, :] = arr2[H2-delta_y:, :, :]
    merged[H1-delta_y:, :, :] = arr2[0:, :, :]

    return merged

"""
merged = merge_images_simple(img_dict["s11.png"]["img_arr"],img_dict["s12.png"]["img_arr"],dy)
s11_s12_merged = Image.fromarray(merged)
s11_12_path =img_dir + "s11_12.png"
s11_s12_merged.save(s11_12_path)
"""

def process_feed(cap1:Capture,cap2:Capture):

    img1 = Image.open(cap1.f_path).convert("RGB")
    arr1 = np.array(img1,dtype=np.uint8)
    img2 = Image.open(cap2.f_path).convert("RGB")
    arr2 = np.array(img2,dtype=np.uint8)
    log("d",f"shape arr1 : {arr1.shape} ; shape arr2 : {arr2.shape}")
    dy = delta_y_between_images(arr1,arr2)
    #shift,error,diffphase = phase_cross_correlation(arr1,arr2)
    #dy = int(shift[0])
    log("d",f"overlap : {dy}")
    merged = merge_images_simple(arr1,arr2,dy)
    log("d",f"shape merge: {merged.shape} ")
    res = Image.fromarray(merged,"RGB")
    #log("d",f"size res : {res.size}")
    

    return res,res.size