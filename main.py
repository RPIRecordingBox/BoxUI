"""
Author: Gavin Song
Email: songc7@rpi.edu
"""

from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget
from pyqt_vertical_tab_widget.verticalTabWidget import VerticalTabWidget
import sys

from views.record import RecordView
from views.info import InfoView
from views.log import LogView
from views.video_test import VideoTestView
from views.mic_test import MicTestView
from views.config import ConfigView

"""
Controls view switching
"""
class Controller(object):
    def __init__(self):
        # self.tabs = VerticalTabWidget()
        self.tabs = QTabWidget()
        
        self.tabs.setAutoFillBackground(True)
        self.current = 0
        
        self.views = [
            RecordView(self),
            LogView(self),
            MicTestView(self),
            VideoTestView(self),
            InfoView(self),
            ConfigView(self)
        ]

        # Spaces are necessary to fake left alignment (as text-align doesn't
        # work on tabs) Also do not use j, g, etc... anything that has a descender
        # because it gets cut off in the tabs
        self.tabs.addTab(self.views[0], "Record   ")
        self.tabs.addTab(self.views[1], "Files    ")
        self.tabs.addTab(self.views[2], "Mic Test ")
        self.tabs.addTab(self.views[3], "Cam Test")
        self.tabs.addTab(self.views[4], "Update")
        self.tabs.addTab(self.views[5], "Config")

        self.views[0].on_open()
        self.tabs.currentChanged.connect(self.switch)

    """
    Switch view to index in self.views
    :param index: zero indexed index
    """
    def switch(self, index):
        self.views[self.current].on_close()
        self.views[index].on_open()
        self.current = index


if __name__ == "__main__":
    app = QApplication([])

    window = QMainWindow()
    window.setAutoFillBackground(True)

    with open("material_dark.qss", "r") as qss:
        qss = qss.read()
        app.setStyleSheet(qss)

    c = Controller()
    window.setCentralWidget(c.tabs)
    
    # info view, only show fullscreen if not in dev branch
    window.show() if c.views[4].is_dev else window.showFullScreen()
    sys.exit(app.exec_())
