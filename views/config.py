from PyQt5.QtWidgets import QLabel, QPushButton, QListWidget, QVBoxLayout, QProgressBar
from src.generic_view import GenericView
import subprocess

"""
Other config options (not including updating)
"""
class ConfigView(GenericView):
    def __init__(self, controller):
        super().__init__(controller)
        
        layout = QVBoxLayout()

        wifi_btn = QPushButton("Open WiFi Settings")
        wifi_btn.setMinimumSize(120, 70)
        wifi_btn.setObjectName("wifiBtn")
        wifi_btn.clicked.connect(self.open_wifi)
        self.wifi_btn = wifi_btn
        layout.addWidget(wifi_btn)

        self.setLayout(layout)

    def open_wifi(self):
        """
        Open linux settings
        """
        subprocess.Popen(["gnome-control-center"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    def on_open(self):
        pass