from PyQt5.QtWidgets import QHBoxLayout, QWidget, QLabel, QPushButton, QListWidget, QVBoxLayout, QProgressBar
import os

from src.config import RECORD_DIR
from src.generic_view import GenericView
from src.storage import storage_used

def size(folder):
    size = 0
    for path, _, files in os.walk(folder):
        for f in files:
            fp = os.path.join(path, f)
            size += os.path.getsize(fp)
    return size

"""
List of recordings
"""
class LogView(GenericView):
    def __init__(self, controller):
        super().__init__(controller)
        
        layout = QVBoxLayout()

        self.storage_label = QLabel("Storage used: ?")
        self.storage_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.storage_label)

        bar = QProgressBar()
        bar.setTextVisible(False)
        bar.setValue(0)
        layout.addWidget(bar)
        self.bar = bar

        listWidget = QListWidget()
        self.listWidget = listWidget
        layout.addWidget(listWidget)

        self.setLayout(layout)
    
    def on_open(self):
        total, used, left = storage_used()
        ratio = used / total
        left = round(left / 1e9)
        total = round(total / 1e9)
        used = round(used / 1e9)
        self.storage_label.setText(f"Storage used: {used} / {total} GB ({left} GB left)")

        c = "red" if ratio > 0.85 else "green"
        self.bar.setValue(ratio * 100)
        self.bar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {c}; }}")

        # Load files
        self.listWidget.clear()
        for dir in [x[0] for x in os.walk(RECORD_DIR)][1:]:
            dname = dir.split("/")[-1]
            self.listWidget.addItem(f"{dname}  - {round(size(dir)  / 1e6, 2)} MB")
