from PyQt5.QtWidgets import QHBoxLayout, QWidget, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import time, datetime, os
from threading import Thread

from src.generic_view import GenericView
from src.storage import storage_used
from src.config import RECORD_DIR
from src.mics import Microphone, mics
from src.video import Cameras
from pathlib import Path

data = []

def perform_recording(folder):
    print(len(mics), "microphones detected")
    mics2 = [Microphone(*x, folder) for x in mics]
    cameras = Cameras([0, 2], folder)

    # Make folder if it doesn't exist
    Path(folder).mkdir(parents=True, exist_ok=True)

    cameras.start()
    for mic in mics2:
        mic.start()

    global data
    data = [cameras] + mics2


"""
Record page
"""
class RecordView(GenericView):
    sig = pyqtSignal()

    def __init__(self, controller):
        super().__init__(controller)

        # State
        self.is_recording = False
        self.record_start = 0
        self.time_since_last_end = 0

        # Layout
        layout = QVBoxLayout()

        time_label = QLabel("0:00:00")
        time_label.setMaximumSize(1200, 120)
        time_label.setObjectName("timeLabel")
        time_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(time_label)
        self.time_label = time_label

        file_label = QLabel("Not currently recording")
        file_label.setMaximumSize(1200, 26)
        file_label.setObjectName("fileLabel")
        file_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(file_label)
        self.file_label = file_label

        storage_label = QLabel("Storage used: ")
        storage_label.setMaximumSize(1200, 26)
        storage_label.setObjectName("storageLabel")
        storage_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(storage_label)
        self.storage_label = storage_label

        start_record_btn = QPushButton("Start Recording")
        start_record_btn.setMinimumSize(240, 160)
        start_record_btn.setObjectName("startBtn")
        start_record_btn.clicked.connect(self.start_recording)
        self.start_record_btn = start_record_btn

        stop_record_btn = QPushButton("Stop Recording")
        stop_record_btn.setObjectName("stopBtn")
        stop_record_btn.setMinimumSize(240, 160)
        stop_record_btn.clicked.connect(self.end_recording)
        self.stop_record_btn = stop_record_btn
        self.stop_record_btn.setEnabled(False)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(start_record_btn)
        btn_layout.addWidget(stop_record_btn)

        widget = QWidget()
        widget.setLayout(btn_layout)

        layout.addWidget(widget)
        self.setLayout(layout)

    def on_open(self):
        self.update_storage()

    def start_recording(self):
        if time.time() - self.time_since_last_end < 2:
            return

        now = datetime.datetime.now()
        dt_string = now.strftime("%d-%m-%Y %H %M %S")

        self.record_start = time.time()
        self.is_recording = True

        self.file_label.setText(dt_string)
        self.time_label.setStyleSheet("color: #3eab4a;")
        self.start_record_btn.setEnabled(False)
        self.stop_record_btn.setEnabled(True)
        Thread(target=self.update_thread).start()

        perform_recording(os.path.join(RECORD_DIR, dt_string))

    def end_recording(self):
        try:
            global data
            for d in data:
                d.stop_record()

            self.time_since_last_end = time.time()
            self.is_recording = False

            # TODO: wait for processing to finish + add processing recording message
            self.start_record_btn.setEnabled(True)
            self.stop_record_btn.setEnabled(False)
            self.time_label.setStyleSheet("color: black;")
        except:
            print("Stop failure... exit")
            self.start_record_btn.setEnabled(True)
            pass

    def update_storage(self):
        total, used, left = storage_used()
        left = round(left / 1e9)
        total = round(total / 1e9)
        used = round(used / 1e9)
        self.storage_label.setText(f"{used} / {total} GB ({left} GB left)")

    def update_thread(self):
        storage_check = time.time()

        while self.is_recording:
            # Update time and storage
            delta = round(time.time() - self.record_start)
            self.time_label.setText(str(datetime.timedelta(seconds=delta)))
            time.sleep(0.5)

            if time.time() - storage_check > 60:
                storage_check = time.time()
                self.update_storage()
