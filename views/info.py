from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout
from PyQt5.QtWidgets import QApplication

from src.generic_view import GenericView
from src.config import *

from packaging import version
import packaging

import subprocess
import datetime
import os
import time


UPDATE_DATA_FILE = "update.txt"

"""
Info and credits, and update
"""
class InfoView(GenericView):
    def __init__(self, controller):
        super().__init__(controller)

        layout = QVBoxLayout()
        label = QLabel(INFO_TEXT)
        label.setAlignment(Qt.AlignTop)
        label.setTextFormat(Qt.RichText)
        self.label = label
        layout.addWidget(label)

        update_btn = QPushButton("Check for Updates")
        update_btn.setMinimumSize(120, 80)
        update_btn.setObjectName("updateBtn")
        update_btn.clicked.connect(self.update)
        self.update_btn = update_btn
        layout.addWidget(update_btn)

        self.setLayout(layout)

        # Update info
        self.last_updated = "Never"
        self.version = "0.0.0"
        self.update_text = ""
        self.is_dev = False
        self.branch = "master"

        self.readUpdateData()
        self.rewriteLabel()


    def getVersionLines(self):
        """
        :return: Array of valid lines only in version.txt
        """
        with open("version.txt", "r") as f:
            lines = f.readlines()
            return [x for x in lines if len(x) and "=" in x]


    def readUpdateData(self):
        """
        Load version & update data into self,
        will create file with defaults
        if it doesn't exist
        """
        if not os.path.exists(UPDATE_DATA_FILE):
            self.writeUpdateData()
    
        # Read update data
        def get_line(lines, i):
            if i >= len(lines):
                return ""
            return lines[i]

        with open(UPDATE_DATA_FILE, "r") as f:
            lines = f.readlines()
            self.last_updated = get_line(lines, 0) or self.last_updated
            self.is_dev = get_line(lines, 1) == "True" or self.is_dev
            self.branch = "dev" if self.is_dev else "master"
        self.writeUpdateData()

        # Read version
        lines, d = self.getVersionLines(), {}
        for line in lines:
            key = line.split("=", 1)[0].strip()
            value = line.split("=", 1)[1].strip()
            d[key] = value
        self.version = d["dev"] if self.is_dev else d["stable"]


    def writeUpdateData(self):
        """
        Write update data into file
        """
        with open(UPDATE_DATA_FILE, "w") as f:
            s = [
                self.last_updated,
                self.is_dev
            ]
            f.write("\n".join([str(x).strip() for x in s]))


    def rewriteLabel(self, updateText="", version=""):
        """
        Update all label text
        :param updateText: Update indicator for user, will use saved if "", and will save
        :param version: Version text, will use saved if ", and will save
        """
        version = version or self.version
        if self.is_dev:
            version += " [dev]"
        updateText = updateText or self.update_text

        text = INFO_TEXT \
            .replace("{version}", version) \
            .replace("{lastUpdated}", self.last_updated) \
            .replace("{update}", updateText)

        self.label.setText(text)
        QApplication.processEvents() # Force label update

        self.update_text = updateText

    
    def parseRequirements(self, override=""):
        """
        Return list of packages in requirements.txt
        :param override: Override package content for testing ONLY
        :return: raw, { name of package: version (if applicable) }
        """
        d = {}
        with open("requirements.txt", "r") as f:
            req = override or f.read()
            for line in req.split("\n"):
                l = line.split("==")
                d[l[0]] = l[1] if len(l) > 1 else ""
            return req, d


    def update(self):
        self.update_btn.setDisabled(True)
        self.rewriteLabel(updateText="<span style=\"color: #AA4400\">Updating, please do not disconnect or poweroff the device</span>")

        # Store original file state
        req, ver = self.parseRequirements()

        p = subprocess.Popen(["git", "pull", "origin", self.branch], stdout=subprocess.PIPE)
        p = p.communicate()[0]
        updated = False

        if not "Already up to date" in str(p):
            # New files, perform update!
            self.rewriteLabel(updateText="<span style=\"color: #AA4400\">Update found, installing...</span>")

            # Execute all version scripts up to this time
            lines = self.getVersionLines()
            for line in lines:
                key = line.split("=")[0].strip()
                if not key.startswith("ver"):
                    continue

                ver = key.split("ver")[1]
                try:
                    if version.parse(ver) > version.parse(self.version):
                        # Attempt to execute new scripts
                        if not 'SUDO_UID' in os.environ.keys():
                            self.rewriteLabel(updateText="<span style=\"color: #FF0000\">Program does not have root access, may not be setup correctly.<br>Update scripts may fail, trying anyways...</span>")

                        cmd = line.split("=", 1)[1].strip().split(" ")
                        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                        p = p.communicate()[0]
                        print(p.decode("utf-8"))
                except packaging.version.InvalidVersion:
                    print(f"Invalid version: {ver} on line '{line}'")

            # Attempt to install new requirements.txt
            req2, ver2 = self.parseRequirements()
            if req2 != req:
                self.rewriteLabel(updateText="<span style=\"color: #AA4400\">Updating python modules...</span>")
         
                # Uninstall any packages that have changed versions
                for package in ver.keys():
                    if ver[package] != ver2.get(package, ""):
                        subprocess.Popen(["python3", "-m", "pip", "uninstall", package, "-y"], stdout=subprocess.PIPE)
                p = subprocess.Popen(["python3", "-m", "pip", "install", "-r", "requirements.txt"], stdout=subprocess.PIPE)
                p = p.communicate()[0]
                print(p.decode("utf-8"))

            self.rewriteLabel(updateText="<span style=\"color: #00AA00\">Update complete, program will restart in 10s</span>")
            updated = True
        else:
            self.rewriteLabel(updateText="<span style=\"color: #00AA00\">Software up to date!</span>")

        self.last_updated = str(datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S"))
        self.writeUpdateData()
        self.rewriteLabel()

        if updated:
            for i in range(10):
                self.rewriteLabel(updateText=f"<span style=\"color: #00AA00\">Update complete, program will restart in {10 - i}s</span>")
                time.sleep(1)
            subprocess.run("./restart.sh", shell=True)
            quit()
        else:
            self.update_btn.setDisabled(False)
