from PyQt5.QtWidgets import QLabel, QPushButton, QListWidget, QVBoxLayout, QProgressBar
from src.generic_view import GenericView

"""
Other config options (not including updating)
"""
class ConfigView(GenericView):
    def __init__(self, controller):
        super().__init__(controller)
        
        layout = QVBoxLayout()


        self.setLayout(layout)
    
    def on_open(self):
        pass