from PyQt5 import QtGui
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtWidgets import QHBoxLayout, QWidget, QLabel, QPushButton, QVBoxLayout, QTableWidget, QMessageBox, \
    QTableWidgetItem, QGridLayout

from src.generic_view import GenericView
from src.config import *

"""
Info and credits
"""
class InfoView(GenericView):
    def __init__(self, controller):
        super().__init__(controller)

        layout = QVBoxLayout()
        label = QLabel(INFO_TEXT)
        label.setAlignment(Qt.AlignTop)
        layout.addWidget(label)

        update_btn = QPushButton("Check for Updates")
        update_btn.setMinimumSize(120, 80)
        update_btn.setObjectName("updateBtn")
        update_btn.clicked.connect(self.update)
        layout.addWidget(update_btn)

        self.setLayout(layout)

    def update(self):
        print(":l")
        pass
