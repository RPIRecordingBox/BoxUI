from PyQt5.QtWidgets import QHBoxLayout, QWidget, QLabel, QVBoxLayout, QProgressBar
from threading import Thread
import time
import numpy as np
from pathlib import Path
import scipy.io.wavfile as wv
import os, shutil

from src.generic_view import GenericView
from src.mics import Microphone, mics
from src.config import CHUNK, MIC_TEMP_FOLDER


def read_moving_average_data():
    """
    Read from temp folder and compute stats
    :return: Array of 4 channels with a number representing the loudness of each
    """
    try:
        levels = [0, 0, 0, 0]
        i = 0

        # Get files in the temp folder
        for _, _, files in os.walk(MIC_TEMP_FOLDER):
            for file in files:
                if not file.endswith(".wav"):
                    continue
                if i > 3:
                    break

                rate, data = wv.read(os.path.join(MIC_TEMP_FOLDER, file))

                # Take last 0.1 s of samples
                t = int(rate * 0.1)
                chan1 = data[:, 0][-t:]
                chan2 = data[:, 1][-t:]

                levels[i] = compute_average(chan1)
                levels[i + 1] = compute_average(chan2)
                i += 2
        return levels
    except ValueError as e:
        # When file is reset it may be empty
        return [0, 0, 0, 0]


def compute_average(data):
    """
    :param data: Wav snippet to compute stat over (single channel)
    :return: Numeric measure of average intensity
    """
    return np.mean(np.abs(data))


"""
Mic test page
"""
class MicTestView(GenericView):
    def __init__(self, controller):
        super().__init__(controller)

        # Make temp folder
        Path(MIC_TEMP_FOLDER).mkdir(parents=True, exist_ok=True)

        # Data
        self.mics = []
        self.open = False
        self.bars = []

        # Layout
        layout = QVBoxLayout()

        def make_mic_line(index):
            layout = QHBoxLayout()

            mic_label = QLabel(f"Mic {index + 1}:")
            mic_label.setMaximumSize(70, 100)
            mic_label.setStyleSheet("font-weight: bold;")

            layout.addWidget(mic_label)
            layout.addWidget(QLabel("Read out text"))
        
            widget = QWidget()
            widget.setLayout(layout)
            return widget

        for i in range(4):
            layout.addWidget(make_mic_line(i))

            bar = QProgressBar()
            bar.setTextVisible(False)
            bar.setValue(50)
            layout.addWidget(bar)
            layout.addStretch()
            self.bars.append(bar)

        self.setLayout(layout)
    
    def on_open(self):
        Path(MIC_TEMP_FOLDER).mkdir(parents=True, exist_ok=True)

        self.perform_recording()
        self.open = True
        Thread(target=self.update_beats).start() # 

    def on_close(self):
        self.open = False
        for mic in self.mics:
            mic.stop_record()
        shutil.rmtree(MIC_TEMP_FOLDER)

    def perform_recording(self):
        mics2 = [Microphone(*x, None) for x in mics]
        for mic in mics2:
            mic.start()
        self.mics = mics2

    def update_beats(self):
        while self.open:
            time.sleep(0.05)
            levels = read_moving_average_data()
            for i, bar in enumerate(self.bars):
                val = levels[i]
                percent = max(0, min(100, val / 700 * 100))
                bar.setValue(percent)
