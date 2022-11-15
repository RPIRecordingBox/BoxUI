'''
Author: Zhengye Yang
Email: yangz15@rpi.edu
Purpose: GUI for STRONG video collection
Last modified date: 04/07/2022
'''
from PyQt5 import QtGui
import os
from PyQt5.QtGui import QPixmap,QIcon,QFont
import sys
import cv2
import shutil
import glob
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread,QSize
import numpy as np
from PyQt5.QtWidgets import QHBoxLayout, QWidget, QApplication, QLabel, QVBoxLayout,\
    QMainWindow, QPushButton,QMessageBox,QGridLayout,QTableWidget,QTableWidgetItem


# TODO seperate
from mics import Microphone, mics
from video import Cameras
from pathlib import Path

from datetime import datetime
import time

data = []
time_since_last_end = 0


def perform_recording(folder):
    print(len(mics), "microphones detected")
    mics2 = [Microphone(*x, folder) for x in mics]
    cameras = Cameras([0, 2], folder)

    # Make folder if it doesn't exist
    Path(folder).mkdir(parents=True, exist_ok=True)

    cameras.start()
    for mic in mics2:
        mic.start()

    global data
    data = [cameras] + mics2


class Record_page(QWidget):
    switch_main_window = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Recording Page')
        self.setGeometry(80,0,720,440)
        self.setWindowIcon(QtGui.QIcon('media_src/strong_icon.jpeg'))
        self.setAutoFillBackground(True)
        self.total_disk, self.used_disk,self.free_disk = shutil.disk_usage('./')
        self.GB_covert = 1024**3
        self.storage_warning = 100 #100 GB

        main_layout = QHBoxLayout()
        layout_1 = QVBoxLayout()
        layout_2 = QVBoxLayout()
        self.disply_width = 640
        self.display_height = 480
    
        # Record button 
        self.start_record_button = QPushButton('Record')
        self.start_record_button.setStyleSheet(
                            "QPushButton"
                             "{"
                             "background-color : green;font-size:36px"
                             "}"
                             "QPushButton::pressed"
                             "{"
                            "background-color : darkgreen;"
                             "}"
                             )
        self.start_record_button.setFixedSize(300,200)
        self.start_record_button.clicked.connect(self.record_start)
        self.stop_record_button = QPushButton('Stop recording')
        self.stop_record_button.setStyleSheet("QPushButton"
                             "{"
                             "background-color : darkred;;font-size:36px"
                             "}"
                             "QPushButton::pressed"
                              "{"
                            "background-color : red;"
                             "}"
                             )
        self.stop_record_button.clicked.connect(self.record_stop)
        self.stop_record_button.setFixedSize(300,200)
        self.stop_record_button.setEnabled(False)
        self.back_main_button = QPushButton('Back to main page')
        self.back_main_button.clicked.connect(self.switch)
        self.back_main_button.setStyleSheet("QPushButton"
                             "{"
                             "background-color : blue;;font-size:36px"
                             "}"
                             "QPushButton::pressed"
                              "{"
                            "background-color : lightblue;"
                             "}"
                             )
        self.back_main_button.setFixedSize(300,200)
        # self.back_main_button.adjustSize()
        self.font = QFont()
        self.font.setBold(True)
        self.disk_table = QTableWidget()
        self.disk_table.setRowCount(3)
        self.disk_table.setColumnCount(2)
        self.disk_table.setColumnWidth(0,150)
        self.disk_table.setColumnWidth(1,150)
        self.disk_table.setRowHeight(0,50)
        self.disk_table.setRowHeight(1,50)
        self.disk_table.setRowHeight(2,50)
        self.disk_table.setFixedSize(300,200)
        self.disk_table.setHorizontalHeaderLabels(['Disk Usage Monitor','Space'])
        self.msg = QMessageBox()
        self.msg.setWindowTitle("Warning")
        self.msg.setText("Disk storage is below "+ str(self.storage_warning)+" GB, please release")
        if round(self.free_disk/self.GB_covert,2) <self.storage_warning:
            self.msg.exec_()
        self.disk_table.setItem(0,0, QTableWidgetItem('Total space:'))
        self.disk_table.item(0,0).setFont(self.font)
        self.disk_table.setItem(0,1, QTableWidgetItem(str(round(self.total_disk/self.GB_covert,2))+' GB'))
        self.disk_table.setItem(1,0, QTableWidgetItem('Used space:'))
        self.disk_table.item(1,0).setFont(self.font)
        self.disk_table.setItem(1,1, QTableWidgetItem(str(round(self.used_disk/self.GB_covert,2))+' GB'))
        self.disk_table.setItem(2,0, QTableWidgetItem('Free space:'))
        self.disk_table.item(2,0).setFont(self.font)
        self.disk_table.setItem(2,1, QTableWidgetItem(str(round(self.free_disk/self.GB_covert,2))+' GB'))
    
        self.record_status_icon = QIcon('./media_src/record_icon.jpg')
        # text_layout.addWidget(self.text_label1)
        # text_layout.addWidget(self.text_label2)
        layout_1.addWidget(self.start_record_button)
        layout_1.addWidget(self.stop_record_button)
        # main_layout.addLayout(vbox)
        layout_2.addWidget(self.disk_table)
        layout_2.addWidget(self.back_main_button)
        main_layout.addLayout(layout_1)
        main_layout.addLayout(layout_2)
        self.setLayout(main_layout)
        
    
        self._stop_flag = False

    def check_space(self):
        self.total_disk, self.used_disk,self.free_disk = shutil.disk_usage('./')
        self.disk_table.setItem(0,0, QTableWidgetItem('Total space:'))
        self.disk_table.item(0,0).setFont(self.font)
        self.disk_table.setItem(0,1, QTableWidgetItem(str(round(self.total_disk/self.GB_covert,2))+' GB'))
        self.disk_table.setItem(1,0, QTableWidgetItem('Used space:'))
        self.disk_table.item(1,0).setFont(self.font)
        self.disk_table.setItem(1,1, QTableWidgetItem(str(round(self.used_disk/self.GB_covert,2))+' GB'))
        self.disk_table.setItem(2,0, QTableWidgetItem('Free space:'))
        self.disk_table.item(2,0).setFont(self.font)
        self.disk_table.setItem(2,1, QTableWidgetItem(str(round(self.free_disk/self.GB_covert,2))+' GB'))
        if round(self.free_disk/self.GB_covert,2) <self.storage_warning:
            self.msg.exec_()

    def record_start(self):
        global time_since_last_end
        if time.time() - time_since_last_end < 2:
            return

        self.check_space()
        self.start_record_button.setEnabled(False)
        self.start_record_button.setIcon(self.record_status_icon)
        self.start_record_button.setIconSize(QSize(100,100))
        self.stop_record_button.setEnabled(True)

        now = datetime.now()
        dt_string = now.strftime("%d-%m-%Y %H %M %S")
        perform_recording(dt_string)
        

    def record_stop(self):
        self.check_space()
        try:
            global data
            for d in data:
                d.stop_record()

            global time_since_last_end
            time_since_last_end = time.time()

            self.stop_record_button.setEnabled(False)
            self.start_record_button.setIcon(QIcon())
            self.start_record_button.setEnabled(True)
            self._stop_flag = True
        except:
            print("Stop failure... exit")
            self.start_record_button.setEnabled(True)
            pass

    def switch(self):
        self.switch_main_window.emit()


class Controller_page():
    #controller page 
    def __init__(self) -> None:
        pass

    def show_home_page(self):
        try:
            self.view_page.close()
            
        except AttributeError:
            # print('can not close view page')
            pass
        try:
            self.realtime_page.close()
            
        except AttributeError:
            pass
        try:
            self.record_page.close()
            
        except AttributeError:
            # print('can not close record page')
            pass
        self.main_page = Record_page()
        #self.main_page.switch_preview_window.connect(self.show_view)
        #self.main_page.switch_recording_window.connect(self.show_record)

        self.main_page.show()

    def show_record(self):
        self.record_page = Record_page()
        self.main_page.close()
        # try: 
        #     self.view_page.close()
        # except: 
        #     pass
        self.record_page.switch_main_window.connect(self.show_home_page)
        self.record_page.show()

