from flask import Flask,request,jsonify,Response
from flask_socketio import SocketIO,emit
import requests
import numpy as np
import cv2

import socket

import pgm.contract



app = Flask(__name__)

open_cv_addr = "http://localhost:5001/trt_image"
overlay_addr = "http://localhost:5002/recieve_data"
default_model = "llama3"
ollama_addr = "http://localhost:11434/api/generate"
default_process_addr = "http://localhost:5000/process_image"

default_prompt = "get info about the following text a give back those info as json. Answer only with the json nothing more . Don't give back the text only informations ! Here is the text :"


""" pretty ugly just a thought on how to deal with incoming message"""
class Sender_handler:
    rhid = 0
    def __init__(self):
        self.senders = {}
    
    def add_sender(self,reciever):
        self.senders[reciever.sender_id] = reciever

    def check_reciever(self,reciever):
        flag = False
        existing_reciever = None
        for s_id,r in self.recievers.items():
            if s_id == reciever.sender_id:
                existing_reciever = reciever 
                flag = True
        if flag == False:
            self.add_sender(reciever)
        else :
            existing_reciever = existing_reciever + reciever

class ContentStructure:
    def __init__(self,content):
        self.content = content
        # import py file ?
        self.structure = ["file","process","sid","cid"]
        self.file = self.content["file"]
        self.process = self.content["process"]
        self.sid = self.content["sid"]
        self.context = self.content["context"]
        self.cid = self.content["cid"]
        self.extracted = {}

    def extract_content(self):
        for key in self.structure:
            setattr(self, key, self.content.get(key))
            self.extracted[key] = getattr(self, key)

class Reciever:
    rid = 0
    def __init__(self,sender_id,content):
        self.sender_id = sender_id
        self.reciever_id = Reciever.rid
        self.content = content
        Reciever_id +=1
    
    def __add__(self,other):
        # add content of previous one ?
        pass
    


class Reciever_Handler:
    def __init__(self):
        self.recievers={}
    
    def add_reciever(self,reciever):
        for i,j in self.recievers.items():
            if i == reciever.rid:
                pass

@app.route("/portal",methods=["POST"])
def portal():
    # must concieve portal so that it handle different process and route them accordingly
    file = request.file["image"]
    data = request.form.to_dict()
    for i,j in data.items():
        print(f"{i} : {j}")
    # single cap case
    if data["process"] == "default":
        print("in default process")
        files = {"image":(file.filename,file.stream,file.content_type)}
        response = requests.post(default_process_addr,files=files,data=data)
    else :
        response = Response(status=500,text=f"route {data['process']} not implemented yet")

    return jsonify({"status":response.status,"message":response.text})


@app.route("/aggregate")
def aggregate():
    pass


@app.route("/process_image",methods=["POST"])
def process_image():


    file = request.files["image"]
    #data = request.get_data()
    data = request.form.to_dict()
    print("data : ",data)
    #img_array = np.frombuffer(file.read(),np.uint8)
    #img = cv2.imdecode(img_array,cv2.IMREAD_COLOR)

    files = {"image":(file.filename,file.stream,file.content_type)}
    print(files)
    response = requests.post(open_cv_addr,files=files)

    print("recieved an image !")

    #return jsonify({"height":img.shape[0],"width":img.shape[1]})
    return jsonify({"status":response.status_code,"reponse":response.text})


def send_data_to_overlay(data, host='127.0.0.1', port=5002):
    print("data to send : ",data)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        #s.sendall(f"{data}".encode)
        s.sendall(data.encode())
        #s.sendall(data)

# streaming = false : allow to get the whole text in one single response !
def make_prompt(txt_to_handle="",prompt=default_prompt,model = default_model):
    #print("prompt : ",prompt)
    prompt = prompt + "\n" +txt_to_handle
    print(f"making prompt : \n{prompt}")
    data = {"prompt":prompt,"model":model,"stream":False}
    response = requests.post(ollama_addr,json=data)
    print(response.json())
    return response.json()["response"]

@app.route("/cv_txt",methods=["POST"])
def cv_txt():
    print("into cv_txt")
    data = request.data
    data = data.decode("utf-8")
    print(data)
    #response = requests.post(overlay_addr,data)

    #return jsonify({"status":response.status_code,"reponse":response.text})
    #send_data_to_overlay(data)
    #send_data_to_overlay("processing text")
    
    result = {"result":make_prompt(data),"from_server":"done"}
    #result = '{"result":{"title":"here is a test","message":"here shoud be the answer of the llm","dict":{"revelance":0,"score":0}},"from_server":{"message":0,"wait_for":0}}'
    #result = '{"title":"here is a test","message":"here shoud be the answer of the llm","dict":{"revelance":0,"score":0}}'
    #result = make_prompt(data)
    
    #print(result)
    result = f"{result}"
    send_data_to_overlay(result)
    

    return jsonify({"status":200,"message":"OK sending back to overlay"})
"""
@socketio.on('connect')
def handle_connect():
    emit('message',{'data':"hey pyqt it's handler !"})
"""
if __name__ == "__main__":
    app.run(host="127.0.0.1",port=5000,debug=True)
