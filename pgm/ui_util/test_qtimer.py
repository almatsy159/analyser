from PyQt5.QtCore import QTimer, pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget


class Controller(QObject):
    stop_signal = pyqtSignal()  # custom signal to stop timer

if __name__ == "__main__":
    app = QApplication([])

    window = QWidget()
    layout = QVBoxLayout(window)

    label = QLabel("Waiting...")
    layout.addWidget(label)

    start_button = QPushButton("Start Timer")
    stop_button = QPushButton("Stop Timer")
    layout.addWidget(start_button)
    layout.addWidget(stop_button)

    window.show()

    # Create timer
    timer = QTimer()
    timer.setInterval(500)  # 1000 ms = 1 second

    # Function to trigger periodically
    def update_label():
        label.setText("Tick...")

    # Connect timer timeout to function
    timer.timeout.connect(update_label)

    # Start button starts the timer
    start_button.clicked.connect(lambda: timer.start())

    # Stop button stops the timer
    stop_button.clicked.connect(lambda: timer.stop())


    app.exec_()

