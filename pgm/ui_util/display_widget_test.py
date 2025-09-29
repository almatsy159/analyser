import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QToolButton, QLabel, QSizePolicy, QPushButton
)
from PyQt5.QtCore import Qt


class DisplayInfo(QWidget):
    def __init__(self, infos):
        super().__init__()
        self.setWindowTitle("Minimal DisplayInfo")

        layout = QVBoxLayout(self)

        # Close button at the top
        close_btn = QPushButton("Close", self)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        # Build top-level dict view
        widget = self.create_info_widget(infos, parent=self)
        layout.addWidget(widget)

        self.setLayout(layout)
    def create_info_widget(self, my_dict, parent=None):
        """Recursive builder for dict -> collapsible widget (accordion style)"""
        container = QWidget(parent)
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)

        buttons = []  # keep track of toggle buttons at this level

        for k, v in my_dict.items():
            if isinstance(v, dict):
                toggle = QToolButton(container)
                toggle.setText(str(k))
                toggle.setCheckable(True)
                toggle.setChecked(False)
                toggle.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
                toggle.setArrowType(Qt.RightArrow)
                vbox.addWidget(toggle)
                buttons.append(toggle)

                sub_widget = self.create_info_widget(v, parent=container)
                sub_widget.setVisible(False)
                vbox.addWidget(sub_widget)

                def on_toggle(checked, btn=toggle, widget=sub_widget):
                    # Collapse siblings
                    for sibling in buttons:
                        if sibling is not btn:
                            sibling.setChecked(False)
                    # Show/hide this widget
                    widget.setVisible(checked)
                    btn.setArrowType(Qt.DownArrow if checked else Qt.RightArrow)
                    container.layout().update()

                toggle.toggled.connect(on_toggle)

            else:
                label = QLabel(f"{k}: {v}", container)
                label.setStyleSheet("color: white;")
                vbox.addWidget(label)

        return container


    def create_info_widget2(self, my_dict, parent=None):
        """Recursive builder for dict -> collapsible widget"""
        container = QWidget(parent)
        vbox = QVBoxLayout(container)

        for k, v in my_dict.items():
            if isinstance(v, dict):
                toggle = QToolButton(container)
                toggle.setText(str(k))
                toggle.setCheckable(True)
                toggle.setChecked(False)
                toggle.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
                toggle.setArrowType(Qt.RightArrow)
                vbox.addWidget(toggle)

                sub_widget = self.create_info_widget(v, parent=container)
                sub_widget.setVisible(False)
                vbox.addWidget(sub_widget)
                def on_toggle(checked, btn=toggle, widget=sub_widget):
                    widget.setVisible(checked)
                    btn.setArrowType(Qt.DownArrow if checked else Qt.RightArrow)
                toggle.toggled.connect(on_toggle)

            else:
                label = QLabel(f"{k}: {v}", container)
                label.setStyleSheet("color: white;")
                vbox.addWidget(label)

        return container


if __name__ == "__main__":
    app = QApplication(sys.argv)

    default_infos3 = {"analyser":{"app":{"tips":{"actions":"to make an action press ctrl+alt then a key in the actions list"},
                         "shortcuts":{"quit":"ctrl+esc","actions":"ctrl+alt+<key>"},
                         "actions":{"single capture":"c","feed capture":"f","video capture":"v","stop video caputre":"s"}},
                "context":"",
                "infos":""}}


    win = DisplayInfo(default_infos3)
    win.show()
    sys.exit(app.exec_())
