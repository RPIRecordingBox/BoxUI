from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QListWidget, QVBoxLayout, QProgressBar, QAbstractItemView, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer

import os, shutil
from datetime import datetime
import subprocess
from threading import Thread

from src.config import RECORD_DIR
from src.generic_view import GenericView
from src.storage import storage_used

def size(folder):
    size = 0
    for path, _, files in os.walk(folder):
        for f in files:
            fp = os.path.join(path, f)
            size += os.path.getsize(fp)
    return size


COPY_BTN_TEXT = "Copy selected to SD card"
CANCEL_COPY_TEXT = "Cancel copy (won't del. files)"
LARGE_COPY_TOTAL = 1e15


"""
List of recordings
"""
class LogView(GenericView):
    def __init__(self, controller):
        super().__init__(controller)
        
        layout = QVBoxLayout()

        self.storage_label = QLabel("Storage used: ?")
        self.storage_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.storage_label)

        bar = QProgressBar()
        bar.setTextVisible(False)
        bar.setValue(0)
        layout.addWidget(bar)
        self.bar = bar

        listWidget = QListWidget()
        listWidget.setSelectionMode(QAbstractItemView.MultiSelection)
        listWidget.itemClicked.connect(self.update_btn_allow)
        self.listWidget = listWidget
        layout.addWidget(listWidget)

        # Warning / success label for copying
        label = QLabel("")
        label.setAlignment(Qt.AlignTop)
        label.setTextFormat(Qt.RichText)
        self.label = label
        layout.addWidget(label)

        # Copy and delete btns
        btn_layout = QHBoxLayout()

        copy_to_sd_btn = QPushButton(COPY_BTN_TEXT)
        copy_to_sd_btn.setMinimumSize(120, 70)
        copy_to_sd_btn.setObjectName("copyToSDBtn")
        copy_to_sd_btn.clicked.connect(self.copy_to_sd_card_btn)
        copy_to_sd_btn.setDisabled(True)
        self.copy_to_sd_btn = copy_to_sd_btn
        btn_layout.addWidget(copy_to_sd_btn)

        del_btn = QPushButton("Del")
        del_btn.setMaximumSize(120, 70)
        del_btn.setObjectName("delBtn")
        del_btn.setDisabled(True)
        del_btn.clicked.connect(self.delete_files)
        self.del_btn = del_btn
        btn_layout.addWidget(del_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

        self.to_copy = []
        self.is_copying = False
        self.copy_thread = None
        self.kill_copy = False
        self.copy_total = LARGE_COPY_TOTAL # Make a large number so default progress is 0%

        timer = QTimer()
        timer.timeout.connect(self.check_upload_progress)
        timer.start(1000)
        self.timer = timer


    def copy_to_sd_card_btn(self):
        """
        Runs when copying to SD card. If not in cancel mode performs copy,
        otherwise cancels the copy
        """
        if self.is_copying:
            if self.copy_thread:
                self.kill_copy = True
                self.copy_thread = None
                self.stop_copy_cleanup()
                self.label.setText(f"<span style='color: #aa0000'>Copy operation was cancelled</span>")
                self.label.repaint()
        else:
            self.copy_to_sd()

    
    def check_upload_progress(self):
        """
        Update progress label when copying a file
        Only to be performed in a background timer
        """
        if not self.is_copying:
            return

        total = self.copy_total
        done = 0
        for p in self.to_copy[1]:
            done += size(os.path.join(self.to_copy[0], p))
        
        percent = min(done * 100 / total, 99.99)
        self.label.setText(f"<span style='color: #777'>{round(percent, 2)}% - Copying {len(self.to_copy[1])} folder(s)..., may take a while, do not remove SD card...</span>")
        self.label.repaint()

    
    def stop_copy_cleanup(self):
        """
        Cleanly set flags after stopping a copy
        """
        self.to_copy = []
        self.is_copying = False
        self.copy_to_sd_btn.setText(COPY_BTN_TEXT)
        self.copy_total = LARGE_COPY_TOTAL
    

    def copy_to_sd(self):
        """
        Copy selected contents of the recording directory into the
        SD folder
        """
        
        # No SD card detected
        p = subprocess.Popen(["lsblk", "/dev/mmcblk0p1"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p = p.communicate()
        p = (p[0] or p[1]).decode("utf-8").strip()

        if "not a block device" in p:
            # No SD card found
            self.label.setText("<span style='color: #aa0000'>No SD card found</span>")
            return

        dir = p.split(" ")[-1]

        if not "/media" in dir:
            # Invalid path error (Shouldn't happen)
            self.label.setText(f"<span style='color: #aa0000'>Unknown error: invalid path '{dir}'</span>")
            return

        sel = self.get_selected()
        self.to_copy = [dir, sel]
        self.label.setText(f"<span style='color: #777'>Copying {len(sel)} folder(s)..., may take a while, do not remove SD card...</span>")
        QApplication.processEvents() # Force label update

        def perform_copy():
            # Copy files over
            def kill_check(path, names):
                if self.kill_copy:
                    return names
                return []

            for p in sel:
                try:
                    dst = os.path.join(dir, p)
                    if os.path.exists(dst):
                        shutil.rmtree(dst)

                    # Compute here due to race condition with thread displaying file size of existing files
                    if self.copy_total >= LARGE_COPY_TOTAL:
                        self.copy_total = 0
                        for p in sel:
                            self.copy_total += size(p)
                    
                    shutil.copytree(p, dst, ignore=kill_check)

                    if self.kill_copy:
                        return
                except OSError as exc:
                    self.stop_copy_cleanup()
                    self.label.setText(f"<span style='color: #aa0000'>OSError during copying: '{exc}'</span>")
                    return

            self.label.setText(f"<span style='color: #00aa00'>Copied {len(sel)} folder(s)!</span>")
            self.stop_copy_cleanup()

        self.copy_to_sd_btn.setText(CANCEL_COPY_TEXT)
        self.is_copying = True
        self.copy_thread = Thread(target = perform_copy)
        self.copy_thread.start()


    def delete_files(self):
        """
        Deleted selected files
        """


    def get_selected(self):
        """
        Get a list of folder dir paths selected
        :return: [list of str of possibly relative but full paths to recordings on device]
        """
        selected = [x.text().split("  ")[0] for x in self.listWidget.selectedItems()]
        return [os.path.join(RECORD_DIR, d.replace(".../", "")) for d in selected]

    
    def update_btn_allow(self):
        """
        Disable buttons when nothing is selected
        """
        disable = len(self.listWidget.selectedItems()) == 0
        if not self.is_copying:
            self.copy_to_sd_btn.setDisabled(disable)
        self.del_btn.setDisabled(disable)


    def on_open(self):
        total, used, left = storage_used()
        ratio = used / total
        left = round(left / 1e9)
        total = round(total / 1e9)
        used = round(used / 1e9)
        self.storage_label.setText(f"Storage used: {used} / {total} GB ({left} GB left)")

        c = "red" if ratio > 0.85 else "green"
        self.bar.setValue(ratio * 100)
        self.bar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {c}; }}")

        # Load files
        self.listWidget.clear()

        # Sort by filename (date wise)
        files = [x[0] for x in os.walk(RECORD_DIR)][1:]
        files.sort(key = lambda row: datetime.strptime(row.split(" ")[0].split("/")[-1], '%d-%m-%Y'), reverse=True)
    
        for dir in files:
            dname = dir.split("/")[-1]

            dir_size = size(dir)
            is_gb = dir_size > 1e9
            size1 = dir_size / 1e9 if is_gb else dir_size / 1e6
            size2 = "GB" if is_gb else "MB"

            def format_file_name(name: str) -> str:
                """
                Format name as better time
                :param name: DD-MM-YYYY HH MM SS
                :return: YYYY/MM/DD HH:MM:SS [AM|PM]
                """
                name = name.split(" ", 1)
                year = [int(x) for x in name[0].split("-")]
                time = [int(x) for x in name[1].split(" ")]
                time_of_day = "AM"

                if time[0] > 12:
                    time_of_day = "PM"
                    time[0] -= 12

                # Add leading zeros
                year = [str(x).zfill(2) for x in year]
                time = [str(x).zfill(2) for x in time]
                year = "/".join(year[::-1])
                time = ":".join(time)

                return f"{year} {time} {time_of_day}"

            self.listWidget.addItem(f".../{dname}       {format_file_name(dname)}        {round(size1, 2)} {size2}")
