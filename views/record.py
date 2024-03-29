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
        
        # Initialize recording
        # camera_1 = Cameras(0, 30, folder)

        # Layout
        layout = QVBoxLayout()
        max_width = 1920
        time_label = QLabel("0:00:00")
        time_label.setMaximumSize(max_width, 260)
        # time_label.setStyleSheet("font-size: 120pt;")
        time_label.setObjectName("timeLabel")
        time_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(time_label)
        self.time_label = time_label

        file_label = QLabel("Not recording")
        file_label.setMaximumSize(max_width, 100)
        # file_label.setStyleSheet("font-size: 48pt;")
        file_label.setObjectName("fileLabel")
        file_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(file_label)
        self.file_label = file_label

        storage_label = QLabel("Storage used: ")
        storage_label.setMaximumSize(max_width, 100)
        # storage_label.setStyleSheet("font-size: 48pt;")
        storage_label.setObjectName("storageLabel")
        storage_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(storage_label)
        self.storage_label = storage_label

        start_record_btn = QPushButton("Start Recording")
        # start_record_btn.setStyleSheet("font-size: 48pt;")
        start_record_btn.setMinimumSize(240, 160)
        start_record_btn.setObjectName("startBtn")
        start_record_btn.clicked.connect(self.start_recording)
        self.start_record_btn = start_record_btn

        stop_record_btn = QPushButton("Stop Recording")
        # stop_record_btn.setStyleSheet("font-size: 48pt;")
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

        # Note: if you change this string you will need to rewrite all the code
        # in log.py that assumes the format of this string
        now = datetime.datetime.now()
        dt_string = now.strftime("%d-%m-%Y %H %M %S")

        self.record_start = time.time()
        self.is_recording = True

        self.file_label.setText(dt_string)
        self.time_label.setStyleSheet("color: #3eab4a;")
        self.start_record_btn.setEnabled(False)
        self.stop_record_btn.setEnabled(True)
        Thread(target=self.update_thread).start()

        # perform_recording(os.path.join(RECORD_DIR, dt_string))
        path = os.path.join(RECORD_DIR, dt_string)
        
        # Make folder if it doesn't exist
        Path(path).mkdir(parents=True, exist_ok=True)
        
        print(len(mics), "microphones detected")
        self.mics2 = [Microphone(*x, path) for x in mics]
        self.video_thread_1 = Cameras(path, 0) ## top left cam
        self.video_thread_2 = Cameras(path, 2) ## bot right cam

        # cameras.start()
        self.video_thread_1._record_flag = True
        self.video_thread_2._record_flag = True
        self.video_thread_1.start()
        self.video_thread_2.start()
        
        # mic.start()
        for mic in self.mics2:
            mic.start()
        
        

    def end_recording(self):
        try:
            # global data
            # for d in data:
            #     d.stop_record()
            self.video_thread_1.stop_record()
            self.video_thread_2.stop_record()
            for mic in self.mics2:
                mic.stop_record()

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
