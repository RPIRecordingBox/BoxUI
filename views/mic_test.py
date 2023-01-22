from PyQt5.QtWidgets import QHBoxLayout, QWidget, QLabel, QVBoxLayout, QProgressBar
from threading import Thread
import time

from src.generic_view import GenericView
from src.mics import Microphone, mics
from src.config import CHUNK

# def compute_moving_average(data_, i):
#     vals = []

#     for data in data_:
#         value = 0
#         count = 0
#         for j in range(2 * (i % 2), CHUNK, 4):
#             count += 1
#             v = data[j] + data[j + 1] * 256 
#             value += abs(v - 32768) * 5
#         if count == 0:
#             return 0
#         vals.append(value / count)
#     if len(vals) == 0:
#         return 0
#     return sum(vals) / len(vals)

"""
Mic test page
"""
class MicTestView(GenericView):
    def __init__(self, controller):
        super().__init__(controller)

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
        self.perform_recording()
        self.open = True
        # Thread(target=self.update_beats).start()

    def on_close(self):
        self.open = False
        for mic in self.mics:
            mic.stop_record()

    def perform_recording(self):
        mics2 = [Microphone(*x, None) for x in mics]
        for mic in mics2:
            mic.start()
        self.mics = mics2

    # def update_beats(self):
    #     # Doesn't work because of thread syncing
    #     while self.open:
    #         time.sleep(0.1)
    #         for i, bar in enumerate(self.bars):
    #             mic = self.mics[int(i / 2)]
    #             val = compute_moving_average(mic.moving_average, i)
    #             bar.setValue(val / 65535 * 100)
