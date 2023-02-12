from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QApplication

from src.generic_view import GenericView
from src.config import *

from packaging import version
import packaging

import subprocess
import datetime
import os
import time
import requests


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

        btn_layout = QHBoxLayout()

        update_btn = QPushButton("Check for Updates")
        update_btn.setMinimumSize(120, 70)
        update_btn.setObjectName("updateBtn")
        update_btn.clicked.connect(self.update)
        self.update_btn = update_btn
        btn_layout.addWidget(update_btn)

        revert_btn = QPushButton("Revert to previous version")
        revert_btn.setMinimumSize(120, 70)
        revert_btn.clicked.connect(self.revert)
        self.revert_btn = revert_btn
        btn_layout.addWidget(revert_btn)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # Update info
        self.last_updated = "Never"
        self.version = "0.0.0"
        self.update_text = ""
        self.is_dev = False
        self.branch = "master"
        self.root = ""
        self.update_available_text = ""
        self.last_commit_hash = "" # Commit hash of last update before updating
        
        self.revert_last_clicked = 0
        self.revert_click_count = 0

        self.readUpdateData()
        self.checkAvailableUpdate()
        self.rewriteLabel()


    def on_open(self):
        # Reset revert confirmation on switch
        self.revert_click_count = 0
        self.revert_last_clicked = 0
        self.rewriteLabel(updateText=" ")


    def getVersionLines(self, lines=[]):
        """
        :param lines: Lines to read from, if empty will read from version.txt
        :return: Array of valid lines only in version.txt
        """
        if len(lines) == 0:
            with open("version.txt", "r") as f:
                lines = f.readlines()
        return [x for x in lines if len(x) and "=" in x and not x.strip().startswith("#")]


    def getVersionDict(self, lines):
        """
        :param lines: Output of getVersionLines
        :return: Dictionary of key value pairs
        """
        d = {}
        for line in lines:
            key = line.split("=", 1)[0].strip()
            value = line.split("=", 1)[1].strip()
            d[key] = value
        return d
        

    def checkAvailableUpdate(self):
        """
        Check github for version updates
        Sets the update avaliable text
        """
        try:
            data = requests.get(UPDATE_URL).text
            data = self.getVersionLines(data.split("\n")) or self.getVersionLines()
            data = self.getVersionDict(data)
            ver = data["stable"]

            try:
                if version.parse(ver) > version.parse(self.version) and not self.is_dev:
                    # New version found
                    self.update_available_text = f"New stable version {ver} available! Use button below to update<br>"
            except packaging.version.InvalidVersion:
                print(f"Invalid version: {ver}")
        except requests.exceptions.ConnectionError:
            print(f"Failed to connect to update url {UPDATE_URL}")


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
            lines = [l.strip() for l in f.readlines()]
            self.last_updated = get_line(lines, 0) or self.last_updated
            self.is_dev = get_line(lines, 1) == "True" or self.is_dev
            self.last_commit_hash = get_line(lines, 2) or self.last_commit_hash
            self.branch = "dev" if self.is_dev else "master"
        self.writeUpdateData()

        # Read version
        d = self.getVersionDict(self.getVersionLines())
        self.version = d["dev"] if self.is_dev else d["stable"]

        # Check if root
        if not 'SUDO_UID' in os.environ.keys():
            self.root = "<span style=\"color: #FF0000\">No root access, contact support (probably misconfigured)</span>"


    def writeUpdateData(self):
        """
        Write update data into file
        """
        with open(UPDATE_DATA_FILE, "w") as f:
            s = [
                self.last_updated,
                self.is_dev,
                self.last_commit_hash
            ]
            f.write("\n".join([str(x).strip() for x in s]))


    def rewriteLabel(self, updateText="", version="", root=""):
        """
        Update all label text
        :param updateText: Update indicator for user, will use saved if "", and will save
        :param version: Version text, will use saved if ", and will save
        """
        version = version or self.version
        if self.is_dev:
            version += " [dev]"
        updateText = updateText or self.update_text
        root = root or self.root

        if updateText: updateText += "<br>"

        text = INFO_TEXT \
            .replace("{version}", version) \
            .replace("{lastUpdated}", self.last_updated) \
            .replace("{update}", updateText) \
            .replace("{root}", root) \
            .replace("{updateAvail}", self.update_available_text)

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


    def revert(self):
        # Check to ensure user didn't accidentally press this
        MSG1 = f"<span style=\"color: #FF0000\">Timed out, click {CLICKS_TO_REVERT - self.revert_click_count} more times to confirm revert, switch menus to cancel</span>"
        MSG2 = f"<span style=\"color: #FF0000\">Click the button {CLICKS_TO_REVERT - self.revert_click_count} more times to confirm revert, switch menus to cancel</span>"
        
        if time.time() - self.revert_last_clicked > TIME_TO_REVERT:
            self.rewriteLabel(updateText=MSG1 if self.revert_last_clicked > 0 else MSG2)
            self.revert_last_clicked = time.time()
            self.revert_click_count = 1
        else:
            self.revert_click_count += 1
            self.rewriteLabel(updateText=MSG2)
        
        if self.revert_click_count <= CLICKS_TO_REVERT:
            return

        self.update_btn.setDisabled(True)
        self.revert_btn.setDisabled(True)
        self.rewriteLabel(updateText="<span style=\"color: #AA4400\">Reverting, please do not disconnect or poweroff the device</span>")

        # Store original file state
        req, ver = self.parseRequirements()

        # This is placeholder, command should be git reset --hard [self.last_commit_hash]
        p = subprocess.Popen(["echo", "'hello'"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p = p.communicate()
        p = p[0] or p[1]
        print(p)
        
        self.updateInPlace(req)
        self.rewriteLabel(updateText="<span style=\"color: #00AA00\">Revert complete, program will restart in 10s</span>")

        self.writeUpdateData()
        self.rewriteLabel()
        self.restartTimer("Revert complete")


    def update(self):
        self.update_btn.setDisabled(True)
        self.revert_btn.setDisabled(True)
        self.rewriteLabel(updateText="<span style=\"color: #AA4400\">Updating, please do not disconnect or poweroff the device</span>")

        # Store original file state
        req, ver = self.parseRequirements()
        self.last_commit_hash = str(subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]), "utf-8").strip()

        p = subprocess.Popen(["git", "pull", "origin", self.branch], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p = p.communicate()
        p = p[0] or p[1]
        updated = False
        print("Updating from github, ", str(p))

        if "Could not resolve host" in str(p):
            self.rewriteLabel(updateText="<span style=\"color: #AA0000\">Could not connect to github, check internet connection</span>")
            self.update_btn.setDisabled(False)
            self.revert_btn.setDisabled(False)
            return
        elif "fatal" in str(p):
            err = str(p, "utf-8").strip()
            self.rewriteLabel(updateText=f"<span style=\"color: #AA0000\">Error: '{err}', contact support</span>")
            self.update_btn.setDisabled(False)
            self.revert_btn.setDisabled(False)
            return
        elif not "Already up to date" in str(p):
            # New files, perform update!
            self.rewriteLabel(updateText="<span style=\"color: #AA4400\">Update found, installing...</span>")
            self.updateInPlace(req)
            self.rewriteLabel(updateText="<span style=\"color: #00AA00\">Update complete, program will restart in 10s</span>")
            updated = True
        else:
            self.rewriteLabel(updateText="<span style=\"color: #00AA00\">Software up to date!</span>")

        self.last_updated = str(datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S"))
        self.writeUpdateData()
        self.rewriteLabel()

        if updated:
            self.restartTimer("Update complete")
        else:
            self.update_btn.setDisabled(False)
            self.revert_btn.setDisabled(False)


    def restartTimer(self, msg):
        """
        :param msg: Message prefix
        """
        for i in range(10):
            self.rewriteLabel(updateText=f"<span style=\"color: #00AA00\">{msg}, program will restart in {10 - i}s</span>")
            time.sleep(1)
        subprocess.run("./restart.sh", shell=True)
        quit()


    def updateInPlace(self, req):
        """
        Updates requirements and commands after files change
        :param req: Previous contents of requirements.txt
        """

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