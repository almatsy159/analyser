

class DisplayInfo(QWidget):
    def __init__(self,infos=None,parent=None,xi=500,yi=500,w=500,h=500):

        super().__init__(parent)
        self.h = h
        self.w = w
        self.xi = xi
        self.yi = yi
        
        self.setGeometry(self.xi,self.yi,self.w,self.h)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        #self.setAttribute(Qt.WA_TransparentForMouseEvents,True)
        
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(5)
        self.setLayout(self.main_layout)
        
        if infos == None:
            self.infos = {}
        else:
            self.infos = infos
        self.generate_view(self.infos)
        
        self.adjustSize()
        self._drag_active = False
        self._drag_position = QPoint()

    def create_info_widget(self, my_dict=None, previous_layout=None):
        if my_dict is None:
            my_dict = {}

        container_widget = QWidget(self)
        container_layout = QVBoxLayout(container_widget)
        #container_layout.setSpacing(5)

        for k, v in my_dict.items():
            line_widget = QWidget(self)
            line_layout = QVBoxLayout(line_widget)
            line_layout.setSpacing(2)

            if isinstance(v, dict):
                # Create a collapsible button for nested dictionaries
                toggle_button = QToolButton(self)
                toggle_button.setStyleSheet("color: #00aaff; font-weight: bold;")
                toggle_button.setText(str(k))
                toggle_button.setCheckable(True)
                toggle_button.setChecked(False)
                toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
                toggle_button.setArrowType(Qt.RightArrow)

                # Sub-widget for nested content
                sub_widget = self.create_info_widget(v)
                sub_widget.setVisible(False)  # start collapsed

            # Connect toggle
                def on_toggle(checked, widget=sub_widget, button=toggle_button):
                    widget.setVisible(checked)
                    button.setArrowType(Qt.DownArrow if checked else Qt.RightArrow)

                toggle_button.toggled.connect(on_toggle)

                line_layout.addWidget(toggle_button)
                line_layout.addWidget(sub_widget)
            else:
                # Regular key-value line
                h_layout = QHBoxLayout()
                key_label = QLabel(str(k), self)
                key_label.setStyleSheet("color: #00aaff; font-weight: bold;")
                value_label = QLabel(str(v), self)
                value_label.setStyleSheet("color: white;")
                value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                h_layout.addWidget(key_label)
                h_layout.addWidget(value_label)
                #h_layout.addStretch()
                line_layout.addLayout(h_layout)

            #line_layout.addStretch()

            # Line container widget
            line_widget = QWidget(self)
            #line_widget.setAttribute(Qt.WA_TransparentForMouseEvents,True)
            line_widget.setLayout(line_layout)
            line_widget.setStyleSheet("""
                background-color: rgba(0, 0, 100, 150);
                border-radius: 6px;
            """)
            #line_widget.adjustSize()
            #container_widget.adjustSize()
            container_layout.addWidget(line_widget)

        return container_widget

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
        self.adjustSize()
        self.show()

    def set_infos(self,infos=None):
        self.infos = infos
        self.generate_view()
