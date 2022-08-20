from PySide6.QtWidgets import QMainWindow, QApplication, QLabel, QVBoxLayout, QPushButton, QWidget
from PySide6.QtGui import QIcon

import sys, os

basedir = os.path.dirname(__file__)

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Podcasts Export")
        layout = QVBoxLayout()
        label = QLabel("Export your downloaded episodes from Apple Podcasts.")
        label.setMargin(10)
        layout.addWidget(label)

        button1 = QPushButton("Export")
        button1.setIcon(QIcon(os.path.join(basedir, "icons", "hand.png")))
        button1.pressed.connect(self.export_episodes)
        layout.addWidget(button1)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

        self.show()

    def export_episodes(self):
        """ Get all downloaded episodes and copy to target dir. """
        print("Clicked Export.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    app.exec()