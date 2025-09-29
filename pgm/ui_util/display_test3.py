import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QToolButton, QLabel, QPushButton, QScrollArea
)
from PyQt5.QtCore import Qt


class DisplayInfo(QWidget):
    def __init__(self, infos):
        super().__init__()
        self.setWindowTitle("Nested Accordion DisplayInfo")
        self.setStyleSheet("background-color: #2b2b2b; color: white;")
        self.setMinimumSize(200, 300)
        #self.resize(600, 400)

        layout = QVBoxLayout(self)

        # Close button at the top
        close_btn = QPushButton("Close", self)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        # Build top-level dict view
        content_widget = self.create_info_widget(infos)

        # Wrap content in a scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(content_widget)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        layout.addWidget(scroll)

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

        return container


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

    win = DisplayInfo(default_infos)
    win.show()
    sys.exit(app.exec_())
