from PyQt5.QtWidgets import QHBoxLayout, QWidget, QLabel, QVBoxLayout, QGridLayout
from PyQt5.QtGui import QPixmap
from PyQt5 import QtGui
from threading import Thread
import time, cv2

from src.generic_view import GenericView
from src.video import Cameras

IMAGE_WIDTH = 300
IMAGE_HEIGHT = 200

"""
Video Test
"""
class VideoTestView(GenericView):
    def __init__(self, controller):
        super().__init__(controller)

        self.cameras = []
        self.open = False
        self.image_labels = []
        
        layout_main = QVBoxLayout()

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")
        layout_main.addWidget(self.error_label)
        layout_main.addStretch()

        layout = QHBoxLayout()

        im = QPixmap("./thumbnail_placeholder.jpg")
        label = QLabel("??")
        label.setPixmap(im)
        label.setFixedSize(IMAGE_WIDTH, IMAGE_HEIGHT)
        layout.addWidget(label)
        self.image_labels.append(label)

        self.im = QPixmap("./thumbnail_placeholder.jpg")
        label = QLabel("??")
        label.setPixmap(self.im)
        label.setFixedSize(IMAGE_WIDTH, IMAGE_HEIGHT)
        layout.addWidget(label)
        layout.insertStretch(-1, 1)
        self.image_labels.append(label)

        layout_main.addLayout(layout)
        layout_main.addStretch()
        self.setLayout(layout_main)
    
    def on_open(self):
        if self.controller.views[0].is_recording:
            self.error_label.setText("Cannot test cameras when currently recording")
        else:
            self.error_label.setText("")

        self.perform_recording()
        self.open = True
        Thread(target=self.update_beats).start()

    def on_close(self):
        self.open = False
        self.cameras.stop_record()

    def perform_recording(self):
        self.cameras = Cameras([0, 2], None)
        self.cameras.start()

    def update_beats(self):
        while self.open:
            if self.cameras.error:
                self.error_label.setText(self.cameras.error)

            time.sleep(0.1)
            for i, image in enumerate(self.cameras.images):
                if i >= 2: break
                image = cv2.resize(image, (IMAGE_WIDTH, IMAGE_HEIGHT))
                image = QtGui.QImage(image.data, image.shape[1], image.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
                self.image_labels[i].setPixmap(QtGui.QPixmap.fromImage(image))
