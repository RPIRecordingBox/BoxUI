from PyQt5.QtWidgets import QHBoxLayout, QWidget, QLabel, QPushButton, QListWidget, QVBoxLayout, QProgressBar
import os
from datetime import datetime

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

        # Sort by filename (date wise)
        files = [x[0] for x in os.walk(RECORD_DIR)][1:]
        files.sort(key = lambda row: datetime.strptime(row.split(" ")[0].split("/")[-1], '%d-%m-%Y'), reverse=True)

    
        for dir in files:
            dname = dir.split("/")[-1]

            dir_size = size(dir)
            is_gb = dir_size > 1e9
            size1 = dir_size / 1e9 if is_gb else dir_size / 1e6
            size2 = "GB" if is_gb else "MB"

            def format_file_name(name: str) -> str:
                """
                Format name as better time
                :param name: DD-MM-YYYY HH MM SS
                :return: YYYY/MM/DD HH:MM:SS [AM|PM]
                """
                name = name.split(" ", 1)
                year = [int(x) for x in name[0].split("-")]
                time = [int(x) for x in name[1].split(" ")]
                time_of_day = "AM"

                if time[0] > 12:
                    time_of_day = "PM"
                    time[0] -= 12

                # Add leading zeros
                year = [str(x).zfill(2) for x in year]
                time = [str(x).zfill(2) for x in time]
                year = "/".join(year[::-1])
                time = ":".join(time)

                return f"{year} {time} {time_of_day}"

            self.listWidget.addItem(f".../{dname}       {format_file_name(dname)}        {round(size1, 2)} {size2}")
