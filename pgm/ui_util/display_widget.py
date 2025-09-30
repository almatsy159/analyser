import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QToolButton, QLabel, QPushButton, QScrollArea
)
from PyQt5.QtCore import Qt,QPoint


class DisplayInfo(QWidget):
    MARGIN = 20  # resize border thicknes
    def __init__(self, infos,parent=None,main=False):
        super().__init__(parent)
        self.setGeometry(500,500,100,100)
        self.setStyleSheet("background-color: rgba(0,0,0,100); color: white;")
        #self.setGeometry(self.xi,self.yi,self.w,self.h)
        if main == True:
            self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        else :
            self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)

        #self.setWindowTitle("Nested Accordion DisplayInfo")
        #self.setStyleSheet("background-color: rgba(0,0,0,155); color: white;")
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)
        self.setMinimumSize(400, 300)
        self.resize(600, 400)
        self.main = main
        self.infos = infos

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        
        # Build top-level dict view
        #content_widget = self.create_info_widget(infos)

        
        self._drag_active = False
        self._drag_position = QPoint()
        self._dragging = False
        self._resizing = False
        self._resize_dir = None
        self.generate_view(main=self.main)

    def create_info_widget(self, my_dict):
        """Recursive builder for dict -> collapsible accordion widget"""
        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)

        toggle_buttons = []  # Track buttons at this level

        for k, v in my_dict.items():
            if isinstance(v, dict):
                toggle = QToolButton()
                toggle.setText(str(k))
                toggle.setCheckable(True)
                toggle.setArrowType(Qt.RightArrow)
                toggle.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
                vbox.addWidget(toggle)
                toggle_buttons.append(toggle)

                sub_widget = self.create_info_widget(v)
                sub_widget.setVisible(False)
                vbox.addWidget(sub_widget)

                def uncheck_children(widget):
                    """Recursively uncheck all toggle buttons inside widget"""
                    for child_btn in widget.findChildren(QToolButton):
                        child_btn.setChecked(False)
                        child_btn.setArrowType(Qt.RightArrow)

                def on_toggle(checked, btn=toggle, widget=sub_widget):
                    if checked:
                        # Collapse all siblings at this level
                        for sibling in toggle_buttons:
                            if sibling is not btn:
                                sibling.setChecked(False)
                        widget.setVisible(True)
                        btn.setArrowType(Qt.DownArrow)
                    else:
                        widget.setVisible(False)
                        btn.setArrowType(Qt.RightArrow)
                        uncheck_children(widget)

                    # Force layout recalculation and propagate size change
                    def update_ancestors(w):
                        if w is None:
                            return
                        w.updateGeometry()
                        w.adjustSize()
                        update_ancestors(w.parentWidget())

                    update_ancestors(container)

                toggle.toggled.connect(on_toggle)

            else:
                label = QLabel(f"{k}: {v}")
                vbox.addWidget(label)
        
        container.setStyleSheet("background-color: rgba(0,0,0,100); color: white;")

        return container
    
    def mousePressEvent(self, event):
        """
        if event.button() == Qt.LeftButton:
            self._drag_active = True
            self._drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        """
        if event.button() == Qt.LeftButton:
            self._resizing, self._resize_dir = self._check_resize_zone(event.pos())
            if self._resizing:
                self._drag_pos = event.globalPos()
                self._geom = self.geometry()
            else:
                self._dragging = True
                self._drag_pos = event.globalPos() -  self.frameGeometry().topLeft()
            event.accept()
    def mouseMoveEvent(self, event):
        if self._resizing:
        # Handle resizing
            delta = event.globalPos() - self._drag_pos
            rect = self._geom
            if "right" in self._resize_dir:
                rect.setRight(rect.right() + delta.x())
            if "bottom" in self._resize_dir:
                rect.setBottom(rect.bottom() + delta.y())
            if "left" in self._resize_dir:
                rect.setLeft(rect.left() + delta.x())
            if "top" in self._resize_dir:
                rect.setTop(rect.top() + delta.y())
            # Enforce minimum size
            rect.setWidth(max(rect.width(), self.minimumWidth()))
            rect.setHeight(max(rect.height(), self.minimumHeight()))
            self.setGeometry(rect)
        elif self._dragging:
            # Handle window dragging
            self.move(event.globalPos() - self._drag_pos)
        else:
            # Hover: update cursor
            _, dir_ = self._check_resize_zone(event.pos())
            if dir_:
                if dir_ in ("left", "right"):
                    self.setCursor(Qt.SizeHorCursor)
                elif dir_ in ("top", "bottom"):
                    self.setCursor(Qt.SizeVerCursor)
                elif dir_ in ("top-left", "bottom-right"):
                    self.setCursor(Qt.SizeFDiagCursor)
                else:
                    self.setCursor(Qt.SizeBDiagCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
            
    def mouseReleaseEvent(self, event):
        self._resizing = False
        self._dragging = False
        self.setCursor(Qt.ArrowCursor)

    def generate_view(self, info_dict=None,main=False):
        if info_dict == None:
            info_dict = self.infos
        # Clear previous widgets
        while self.main_layout.count():
            child = self.main_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        if main == True:
            
            # Close button at the top
            close_btn = QPushButton("Close", self)
            close_btn.clicked.connect(self.close)
            self.main_layout.addWidget(close_btn)
        
 
        
        info_widget = self.create_info_widget(info_dict)

        # Wrap content in a scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setMouseTracking(True)
        scroll.viewport().setMouseTracking(True)
        #scroll.show()

        self.main_layout.addWidget(scroll)
        scroll.setWidget(info_widget)
        #self.main_layout.addWidget(info_widget)
        #self.adjustSize()
        #scroll.show()
        #self.show()
    def set_infos(self,infos=None):
        self.infos = infos
        self.generate_view(main=self.main)

    def _check_resize_zone(self, pos):
        rect = self.rect()
        left = pos.x() <= self.MARGIN
        right = pos.x() >= rect.width() - self.MARGIN
        top = pos.y() <= self.MARGIN
        bottom = pos.y() >= rect.height() - self.MARGIN

        if top and left: return True, "top-left"
        if top and right: return True, "top-right"
        if bottom and left: return True, "bottom-left"
        if bottom and right: return True, "bottom-right"
        if left: return True, "left"
        if right: return True, "right"
        if top: return True, "top"
        if bottom: return True, "bottom"
        return False, None

    
"""   
class MainWidget(QWidget):
    def __init__(self,display_dict):
        super().__init__()
    
    
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        screen = QApplication.primaryScreen()
        size = screen.size()
        self.w = size.width()
        self.h = size.height()
        #self.setAttribute(Qt.WA_TransparentForMouseEvents,True)  # Click-through
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.display_dict = display_dict
        
        self.info_widget = DisplayInfo(default_infos)

        #self.create_interface()
        self.generate_interface()
    
    def generate_interface(self):
 
        self.setup_partial_mode()


    def setup_partial_mode(self):


        self.info_widget.show()

    
    
"""



if __name__ == "__main__":
    app = QApplication(sys.argv)

    default_infos = {
        "analyser": {
            "app": {
                "tips": {
                    "actions": "To make an action, press ctrl+alt then a key in the actions list. "
                               "This text is deliberately long to test the resizing behavior. "
                               "It should scroll if necessary instead of expanding the window too much."
                },
                "shortcuts": {"quit": "ctrl+esc", "actions": "ctrl+alt+<key>"},
                "actions": {
                    "single capture": "c",
                    "feed capture": "f",
                    "video capture": "v",
                    "stop video capture": "s"
                },
            },
            "context": "",
            "infos": "",
        }
    }

    win = DisplayInfo(default_infos,main=True)
    #win = MainWidget(default_infos)
    win.show()
    sys.exit(app.exec_())


