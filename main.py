#!/usr/bin/env python3
#
#  Podcasts Export
#  ---------------
#  Douglas Watson, 2022, MIT License
#
#  Finds Apple Podcasts episodes that have been
#  downloaded, then copies those files into a new folder giving them a more
#  descriptive name.
#
#  main.py: draw GUI and handle GUI events (button clicks, progress display...)


import os
import sys
from PySide6.QtCore import Slot, QThreadPool
from PySide6.QtWidgets import QMainWindow, QApplication, QLabel, QVBoxLayout, QPushButton, QWidget, QProgressBar
from PySide6.QtGui import QIcon

import export
from worker import Worker

basedir = os.path.dirname(__file__)

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Podcasts Export")
        layout = QVBoxLayout()
        label = QLabel("Export your downloaded episodes from Apple Podcasts.")
        label.setMargin(10)
        layout.addWidget(label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)

        self.export_button = QPushButton("Export")
        self.export_button.pressed.connect(self.export_episodes)
        layout.addWidget(self.export_button)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

        self.threadpool = QThreadPool()

        self.show()
        
    def update_progress(self, p):
        print("Progress: {}%".format(p))
        self.progress_bar.setValue(p)

    def export_started(self):
        self.export_button.setDisabled(True)

    def export_finished(self):
        self.export_button.setEnabled(True)
        self.update_progress(100)

    def export_refresh_result(self, result):
        print(result)

    @Slot()
    def export_episodes(self):
        """ Get all downloaded episodes and copy to target dir. """

        worker = Worker(export.export, export.get_db_path(), "/Users/douglas/Desktop/exported") # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.export_refresh_result)
        worker.signals.finished.connect(self.export_finished)
        worker.signals.progress.connect(self.update_progress)

        # Execute
        self.export_started()
        self.threadpool.start(worker)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    app.exec()