from pgm.os_util.get_info import *
from pgm.ui_util.overlay import *
import re 
import time
import json
import subprocess

def get_filename_only(path):
    filename_without_ext = ""
    # Regex to capture filename without extension
    match = re.search(r'/([^/]+)\.[^/.]+$', path)

    if match:
        filename_without_ext = match.group(1)
        print(filename_without_ext)
    return filename_without_ext

def get_dirname_only(path):
    # Regex to capture the filename with extension
    filename=""
    match = re.search(r'([^/]+)$', path)

    if match:
        filename = match.group(1)
        #print(filename)
    
    return filename


def drop_dir(dir_to_empty=None):
    del_flag = False
    if dir_to_empty not in os.listdir("./data"):
        print("can't delete this dir")
        raise FileNotFoundError
    
    else :
        #print(get_dirname_only(os.getcwd()))
        if get_dirname_only(os.getcwd()) == "analyser":
            #res = input(f"do you want to delete (y) ./data/{dir_to_empty} ?\n please make sure you are running from 'analyser' directory !\ncurrent directory is {os.getcwd()}\n")
            res = input(f"do you want to delete (y) ./data/{dir_to_empty}\n")
            if res == "y":
                del_flag = True
        else :
            print("not running from the good directory risk of deleting the wrong file")

    if del_flag == True:
        print("okay then deleting this dir")
        lst = os.listdir(f"./data/{dir_to_empty}")
        res2= input(f"you will delete those files : \n{lst}'\n are you sure ? (y)\n")
        if res2 == "y":
            for f in os.listdir(f"./data/{dir_to_empty}"):
                print(f)
                os.remove(f"./data/{dir_to_empty}/{f}")
    #print(os.getcwd())
    #print(os.listdir("./data"))


def generate_ds_from_txt(path="/home/alma/analyser/data/"):
    res = {"text":{}}
    path_txt = path + "txt/"
    path_ds = path + f"datasets/ds_from_txt.jsonl"

    
    for i,t in enumerate(os.listdir(path_txt)):
        name = t
        with open(f"{path_txt}{t}","r") as f:
            text = f.read()
        #res[i] = {"name":name,"text":text}
        res["text"][i] = text
    
    with open(path_ds,"w+",encoding="utf-8") as f:
        #f.write(f"{res}")
        json.dump(res,f,ensure_ascii=False,indent=4)
        #for idx,item in res.items(): 
        #    json_line = json.dumps(item, ensure_ascii=False)
        #    f.write(json_line)

      
#generate_ds_from_txt()
        

"""
drop_dir("cv2")
drop_dir("models")
drop_dir("txt")
"""
drop_dir("img")





