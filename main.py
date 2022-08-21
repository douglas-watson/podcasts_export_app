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
import pathlib
import datetime

from PySide6.QtCore import Slot, QThreadPool
from PySide6.QtWidgets import QMainWindow, QApplication, QLabel, QGridLayout, QPushButton, QWidget, QProgressBar, \
    QTableWidget, QTableWidgetItem, QAbstractItemView, QLineEdit, QFileDialog, QPlainTextEdit
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
        layout = QGridLayout()
        label = QLabel("Export your downloaded episodes from Apple Podcasts.")
        label.setMargin(10)
        layout.addWidget(label, 0, 0, 1, 3)

        # Destination folder selection
        label = QLabel("Destination Folder:")
        label.setMargin(10)
        layout.addWidget(label, 1, 0)

        self.dest_folder = QLineEdit(os.path.join(pathlib.Path.home(), "Desktop"))
        layout.addWidget(self.dest_folder, 1, 1)

        self.browse_button = QPushButton("Browse...")
        self.browse_button.pressed.connect(self.browse)
        layout.addWidget(self.browse_button, 1, 2)

        # Episodes display
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
        layout.addWidget(self.table, 2, 0, 1, 3)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar, 3, 0, 1, 3)

        # Results
        self.results = QPlainTextEdit()
        self.results.hide()
        layout.addWidget(self.results, 4, 0, 1, 3)

        # Lower buttons
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.pressed.connect(self.get_episodes)
        layout.addWidget(self.refresh_button, 5, 0)

        self.export_button = QPushButton("Export")
        self.export_button.pressed.connect(self.export_episodes)
        layout.addWidget(self.export_button, 5, 2)
        

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

        self.threadpool = QThreadPool()
        self.get_episodes()

        self.show()

    @Slot()
    def browse(self):
        directory = QFileDialog.getExistingDirectory(self, "Choose destination folder", 
            self.dest_folder.text())
        
        if directory:
            self.dest_folder.setText(directory)

    def redraw_episodes(self, episodes):
        """ Fill table from list of episodes """
        self.episodes = episodes
        self.table.clearContents()
        self.table.setSortingEnabled(False)
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

    def export_redraw_result(self, result):
        # TODO: show any errors.
        self.results.show()
        self.results.setPlainText("Results go here.")

    @Slot()
    def get_episodes(self):
        """ Get all downloaded episodes and show in table """
        worker = Worker(export.get_downloaded_episodes) 
        worker.signals.result.connect(self.redraw_episodes)
        # worker.signals.finished.connect(self.export_finished)
        # worker.signals.progress.connect(self.update_progress)

        # Execute
        self.threadpool.start(worker)

    @Slot()
    def export_episodes(self):
        """ Get all downloaded episodes and copy to target dir. """

        worker = Worker(export.export, self.get_selected(), self.dest_folder.text())
        worker.signals.result.connect(self.export_redraw_result)
        worker.signals.finished.connect(self.export_finished)
        worker.signals.progress.connect(self.update_progress)

        # Execute
        self.export_started()
        self.threadpool.start(worker)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    app.exec()