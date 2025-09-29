
class DisplayInfo(QWidget):
    def __init__(self, infos,parent=None,xi=100,yi=100,w=200,h=200):
        super().__init__(parent)
        #self.parent 
        #self.setWindowTitle("Nested Accordion DisplayInfo")
        self.setStyleSheet("background-color: #2b2b2b; color: white;")
        self.xi,self.yi = xi,yi
        self.w,self.h = w,h
        #self.setMinimumSize(200, 300)
        self.move(self.xi,self.yi)

        #self.resize(600, 400)
        self.setGeometry(self.xi,self.yi,self.w,self.h)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.infos= infos
        
        """
        # Close button at the top
        close_btn = QPushButton("Close", self)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        """
        
        # Build top-level dict view
        #content_widget = self.create_info_widget(self.infos)


        self.generate_view(self.infos)
        self.adjustSize()
        

        self._drag_active = False
        self._drag_position = QPoint()

    def create_info_widget(self, my_dict):

        """Recursive builder for dict -> collapsible accordion widget"""
        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)

        #self.main_layout.addWidget(scroll)

        toggle_buttons = []  # Track buttons at this level

        for k, v in my_dict.items():
            if isinstance(v, dict):
                toggle = QToolButton(self)
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
                label = QLabel(f"{k}: {v}",self)
                vbox.addWidget(label)

        # Wrap content in a scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)


        #return container
        return scroll
    
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_active = True
            self._drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_active and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_active = False

    
    def generate_view(self, info_dict=None):
        if info_dict == None:
            info_dict = self.infos
        # Clear previous widgets
        while self.main_layout.count():
            child = self.main_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        info_widget = self.create_info_widget(info_dict)
        self.main_layout.addWidget(info_widget)
        #self.adjustSize()
        self.show()

    def set_infos(self,infos=None):
        self.infos = infos
        self.generate_view()
