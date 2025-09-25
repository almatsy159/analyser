import cv2
import pytesseract
import numpy as np
import os

import threading
import re
import requests

from flask import Flask,request,jsonify

app = Flask(__name__)
handler_addr_txt = "http://localhost:5000/cv_txt"


def get_filename_only(path):
    filename_without_ext = ""
    # Regex to capture filename without extension
    match = re.search(r'/([^/]+)\.[^/.]+$', path)

    if match:
        filename_without_ext = match.group(1)
        print(filename_without_ext)
    return filename_without_ext

@app.route("/trt_image",methods=["POST"])
def trt_image():
    print("in trt image")
    print(request)
    file = request.files["image"]
    file_byte = file.read()
    np_arr = np.frombuffer(file_byte,np.uint8)
    
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #cv2.imwrite("data/gray.png",gray)
   
    text = pytesseract.image_to_string(gray,"eng+fra")
    #print(text)
    #print(path)
    #print(path_to_write_cv2_img)
    path_to_write_cv2_img = get_filename_only(file.filename)
    cv2.imwrite(f"data/cv2/{path_to_write_cv2_img}.png", img)
    #container["blocks"]= blocks
    #print(text)

    with open(f"data/txt/{path_to_write_cv2_img}.txt","w") as f:
        f.write(text)
    
    print("sending text to handler")
    json = {"text":text}
    response = requests.post(handler_addr_txt,json=json)

    print(response.status_code)

    return jsonify({"message":"seem ok but must include tests"})




if __name__ == "__main__":
    app.run(host="127.0.0.1",port=5001,debug=True)