from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QMenu, QAction,
    QTreeWidget, QTreeWidgetItem, QTabWidget, QLabel
)
import sys


class FullModeApp(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Full Mode App")
        self.resize(1000, 600)

        # Main layout (vertical)
        main_layout = QVBoxLayout(self)

        # ---- MenuBar ----
        self.menu_bar = QMenuBar()
        file_menu = QMenu("File", self)
        edit_menu = QMenu("Edit", self)
        help_menu = QMenu("Help", self)

        # Example actions
        new_action = QAction("New Session", self)
        new_action.triggered.connect(self.new_session)

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)

        file_menu.addAction(new_action)
        file_menu.addAction(quit_action)

        edit_menu.addAction(QAction("Preferences", self))
        help_menu.addAction(QAction("About", self))

        self.menu_bar.addMenu(file_menu)
        self.menu_bar.addMenu(edit_menu)
        self.menu_bar.addMenu(help_menu)

        main_layout.setMenuBar(self.menu_bar)

        # ---- Central HBox ----
        central_layout = QHBoxLayout()

        # Left: sessions & captures tree view
        self.session_tree = QTreeWidget()
        self.session_tree.setHeaderHidden(True)
        self.session_tree.itemDoubleClicked.connect(self.open_analysis)

        # Example sessions/captures
        session1 = QTreeWidgetItem(["Session 1"])
        QTreeWidgetItem(session1, ["Capture A"])
        QTreeWidgetItem(session1, ["Capture B"])

        session2 = QTreeWidgetItem(["Session 2"])
        QTreeWidgetItem(session2, ["Capture X"])
        QTreeWidgetItem(session2, ["Capture Y"])

        self.session_tree.addTopLevelItem(session1)
        self.session_tree.addTopLevelItem(session2)

        self.session_tree.expandAll()

        central_layout.addWidget(self.session_tree, 1)

        # Right: main tab area (with closable tabs)
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        central_layout.addWidget(self.tab_widget, 3)

        main_layout.addLayout(central_layout)

    # ---- Functions ----
    def new_session(self):
        print("New session triggered")

    def open_analysis(self, item, column):
        if item.parent() is None:
            # Ignore top-level (sessions), only open captures
            return
        analysis_name = f"{item.parent().text(0)} - {item.text(0)}"
        tab = QLabel(f"Content of {analysis_name}")
        self.tab_widget.addTab(tab, analysis_name)
        self.tab_widget.setCurrentWidget(tab)

    def close_tab(self, index):
        widget = self.tab_widget.widget(index)
        if widget:
            self.tab_widget.removeTab(index)
            widget.deleteLater()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FullModeApp()
    window.show()
    sys.exit(app.exec_())
