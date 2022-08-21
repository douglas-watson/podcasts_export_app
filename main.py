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

# TODO: replace date by a QDateTime?
# TODO: add an Abort button?


import os
import sys
import datetime

from PySide6.QtCore import Slot, QThreadPool
from PySide6.QtWidgets import QMainWindow, QApplication, QLabel, QVBoxLayout, QPushButton, QWidget, QProgressBar, \
    QTableWidget, QTableWidgetItem, QAbstractItemView
from PySide6.QtGui import QIcon

import export
from worker import Worker

basedir = os.path.dirname(__file__)

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # Store the original episode list since QTableWidget messes up the sorting.
        # Easier than using filter proxies...
        self.episodes = []

        self.setWindowTitle("Podcasts Export")
        self.resize(800, 400)
        layout = QVBoxLayout()
        label = QLabel("Export your downloaded episodes from Apple Podcasts.")
        label.setMargin(10)
        layout.addWidget(label)

        self.table = QTableWidget()
        self.table.setRowCount(8)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Author", "Podcast", "Episode", "Date", "Index"])
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 300)
        self.table.setColumnWidth(3, 100)
        self.table.setColumnHidden(4, True) # Keep track of original index
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table)
        
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
        self.get_episodes()

        self.show()

    def refresh_episodes(self, episodes):
        """ Fill table from list of episodes """
        self.episodes = episodes
        self.table.setRowCount(len(episodes))
        for i, ep in enumerate(episodes):
            index = QTableWidgetItem(str(i))
            author = QTableWidgetItem(ep[0])
            podcast = QTableWidgetItem(ep[1])
            title = QTableWidgetItem(ep[2])

            pubdate = datetime.datetime(2001, 1, 1) + datetime.timedelta(seconds=ep[4])
            date = QTableWidgetItem("{:%Y.%m.%d}".format(pubdate))

            self.table.setItem(i, 0, author)
            self.table.setItem(i, 1, podcast)
            self.table.setItem(i, 2, title)
            self.table.setItem(i, 3, date)
            self.table.setItem(i, 4, index)

        self.table.setSortingEnabled(True)

    def get_selected(self):
        selected_rows = [index.row() for index in self.table.selectionModel().selectedRows()]
        selected_indices = [int(self.table.item(i, 4).text()) for i in selected_rows]
        return [self.episodes[i] for i in selected_indices]
        
    def update_progress(self, p):
        self.progress_bar.setValue(p)

    def export_started(self):
        self.export_button.setDisabled(True)

    def export_finished(self):
        self.export_button.setEnabled(True)
        self.update_progress(100)

    def export_refresh_result(self, result):
        # TODO: show any errors.
        print(result)

    @Slot()
    def get_episodes(self):
        """ Get all downloaded episodes and show in table """
        worker = Worker(export.get_downloaded_episodes) 
        worker.signals.result.connect(self.refresh_episodes)
        # worker.signals.finished.connect(self.export_finished)
        # worker.signals.progress.connect(self.update_progress)

        # Execute
        self.threadpool.start(worker)

    @Slot()
    def export_episodes(self):
        """ Get all downloaded episodes and copy to target dir. """

        worker = Worker(export.export, self.get_selected(),"/Users/douglas/Desktop/exported")
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