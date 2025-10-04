from pgm.ui_util.log import log
import re
import json

class Context:
    def __init__(self,window,user):
        self.window = window
        self.user = user
        self.session = None
        self.window_name = self.extract_application_from_window_name()
        self.app_id = None

    def extract_application_from_window_name(self):

        my_match = re.search(r'[-—]\s*([^—\-\n]+)\s*$', self.window["name"])
    
        if my_match : 
            log("s",f"match : {my_match.group(1)}")
            res = re.sub(" ","",my_match.group(1))
        #return my_match.group(1)mmmmmmm

        else :
            log("w","not matched the regex")
            res = re.sub(" ","",self.window["name"])
        log("d",res)
        return res
    
    def change_window(self,window):
        self.window = window
        self.window_name = self.extract_application_from_window_name()
    
    #def to_json(self):
    #    return json.dumps(self.__dict__)
    
    def to_json(self):
        serializable = {k: (list(v) if isinstance(v, tuple) else v) for k,v in self.__dict__.items()}
        return json.dumps(serializable)
