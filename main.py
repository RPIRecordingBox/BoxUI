from gui import Controller_page

import time, sys
from PyQt5.QtWidgets import QApplication

app = QApplication(sys.argv)
app.setStyle('Fusion')

controller = Controller_page()
controller.show_home_page()
sys.exit(app.exec_())
