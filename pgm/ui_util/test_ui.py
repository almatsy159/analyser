from PyQt5.QtWidgets import QApplication, QLabel, QWidget,QVBoxLayout,QHBoxLayout,QSizePolicy,QPushButton
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QFont

# intersting script but not apllicable to overlay (well applicable but not revelant). Generating the ui this way could make it harder to scale...

class Contain_Childs(QWidget):
    def __init__(self,last=True):
        super().__init__()
        self.last = last
        if self.last == False:
            Contain_Childs()






class Overlay(QWidget):
    def __init__(self,mod=0):
        super().__init__()
        self.mod = mod
        self.widgets_param={"contain_child0":{"class":Contain_Childs,"mode":"full","args":[False],"kwargs":{}},"button1":{"class":QPushButton,"mode":"partial","args":[],"kwargs":{"text":"hi"}}}
        self.mod_dict = {"full":{"transparent_mouse_event":False},"partial":{"transparent_mouse_event":True}}
        self.mods = {0:"full",1:"partial"}
        self.widgets= {}
        self.create_interface()
        self.generate_interface()
        

        #self.widgets_full_moode = {QLabel()}
    def create_interface(self):
        for k,v in self.widgets_param.items():
            args = v.get("args", [])
            kwargs = v.get("kwargs", {})
            tmp = v["class"](*args, **kwargs)
            #tmp = v["class"](*v["args"],**v["kwargs"])
            self.widgets[k] = tmp

    def generate_interface(self):
        current_mod = self.mods[self.mod]
        """
        if self.mod == 0:
            label = QLabel(text="mod 0")
            label.show() 
        """
        for k,v in self.widgets_param.items():
            if v["mode"] == self.mods[self.mod]:
                self.set_attr(self.widgets[k],current_mod)
                self.widgets[k].show()
                for c in self.widgets[k].findChildren(QWidget):
                    self.set_attr(c,current_mod)
            else :
                self.widgets[k].hide()
    
    def set_attr(self,widget,mod=None):
        if mod == None:
            mod = self.mods[self.mod]
        for k,v in self.mod_dict[mod].items():
            if k == "transparent_mouse_event":
                widget.setAttribute(Qt.WA_TransparentForMouseEvents,v)
            # other attributes setted up here

    def add_widget(self,widget_dict,id_widget):

        if id_widget in self.widgets:
            print(f"Widget ID '{id_widget}' already exists!")
            return
        self.widgets_param[id_widget] = widget_dict
        tmp = widget_dict["class"](*widget_dict.get("args", []))
        self.widgets[id_widget] = tmp
        # apply current mode attributes immediately
        self.generate_interface()

    def remove_widget(self,id_widget):
        self.widgets[id_widget].hide()
        self.widgets[id_widget].deleteLater()
        del self.widgets_param[id_widget]
        del self.widgets[id_widget]
            



if __name__ == "__main__":
    app = QApplication([])
    overlay = Overlay(1)
    overlay.show()
    app.exec_()