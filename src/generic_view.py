from PyQt5.QtWidgets import QWidget

"""
All views should inherit this
"""
class GenericView(QWidget):
    """
    Initiate a GenericWidget
    :controller: Controller instance this belongs to
    """
    def __init__(self, controller):
        super().__init__()
        self.setGeometry(0, 0, 1920, 1080)
        # self.setFixedWidth(1760)
        self.controller = controller

    """
    Called when this view is switched to
    """
    def on_open(self):
        pass

    """
    Called when this view is swithced from
    """
    def on_close(self):
        pass
