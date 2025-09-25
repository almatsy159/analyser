# allow execution of opencv without conflict with pygt overlay (cause opencv work with pyqt apparently) but cause the overlay to not be activated ...*
# look for qthread to solve this

#os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "0"
#os.environ["QT_QPA_PLATFORM"] = "offscreen"

import cv2
import pytesseract
import numpy as np
import os

import threading
import re


def get_filename_only(path):
    filename_without_ext = ""
    # Regex to capture filename without extension
    match = re.search(r'/([^/]+)\.[^/.]+$', path)

    if match:
        filename_without_ext = match.group(1)
        print(filename_without_ext)
    return filename_without_ext


def process_screenshot(path):
    print(f"processing screenshot {path}")
    img = cv2.imread(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite("data/gray.png",gray)
    # Amélioration du contraste + Binarisation
    #blur = cv2.GaussianBlur(gray, (5,5), 0)
    #cv2.imwrite("data/blur.png",blur)
    #thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
    #                               cv2.THRESH_BINARY_INV, 11, 2)
    #cv2.imwrite(f"data/thresh.png",thresh)

    # Détection des contours (blocs de texte)
    #contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #blocks = []
    """
    print(len(contours))
    blocks = []
    for cnt in contours:
        #print(cnt)
        x, y, w, h = cv2.boundingRect(cnt)
        print(w,h)
        if w > 50 and h > 20:  # Filtre les petits bruits
            roi = img[y:y+h, x:x+w]
            text = pytesseract.image_to_string(roi, lang='eng+fra')
            if text.strip():
                blocks.append({"coords": (x, y, w, h), "text": text.strip()})
                cv2.rectangle(img, (x, y), (x+w, y+h), (0,255,0), 2)
    """
    text = pytesseract.image_to_string(gray,"eng+fra")
    #print(text)
    #print(path)
    path_to_write_cv2_img = get_filename_only(path)
    cv2.imwrite(f"data/cv2/{path_to_write_cv2_img}.png", img)
    #container["blocks"]= blocks
    return text


#container = {}
filename = "screenshot.png"
path = f"data/test/{filename}"
text = process_screenshot(path)
print(text)

#for b in blocks:
#    print(b)

path_to_create_txt = get_filename_only(path)
with open(f"data/txt/{path_to_create_txt}.txt","w") as f:
    f.write(text)
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

