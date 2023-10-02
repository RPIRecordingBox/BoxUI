from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
import numpy as np
import time
import os
import cv2

class Cameras(QThread):
    
    change_pixmap_signal = pyqtSignal(np.ndarray)
    
    def __init__(self, file_path, cam_idex = 0, video_fps = 30, res = (1920, 1080), chunk_duration = 300):
        super().__init__()
        
        ## flags
        self._run_flag = True # to control the video capture reading loop
        self._record_flag = False # write video or not (preview vs. recording mode)
        self.preview = None # placeholder for storing preview image
        
        self.should_stop = False # for control sequence in GUI
        
        # video params
        self.cam_idx = cam_idex
        # self.fps = video_fps
        self.fourcc = 'MJPG' # self.fourcc = 'XVID'
        self.frame_shape = res
        
        # video writer info
        self.start_time = time.time()
        self.file_path = file_path
        self.file_name = os.path.join(file_path, str(self.start_time) + '_cam' + str(self.cam_idx) + '_chunk0_recording.avi')
        self.frame_cnt = 1
        self.chunk_cnt = 0
        self.chunk_duration = chunk_duration
        self.next_cut = self.start_time + self.chunk_duration
        

    def get_output(self, fps, video_out=None):
        """
        set the current chunk video writer
        Specify the path and name of the video file as well as the encoding, fps and resolution
        """
        if video_out:
            video_out.release()
            
        chunk_path = os.path.join(self.file_path, str(self.start_time) + '_cam' + str(self.cam_idx) + '_chunk' + str(self.chunk_cnt) + '_recording.avi')
        
        return cv2.VideoWriter(chunk_path,  self.video_writer, fps, self.frame_shape)
    
    def run(self):
        """
        main function for running the video recording
        """
        # self._record_flag = True
        self._run_flag = True
        
        try: ## if there's a previous video capture session, release memory
            self.cap_rec.release()
        except:
            pass

        ## initialize video capture, specify V4L2 since the machine is linux
        self.cap_rec = cv2.VideoCapture(self.cam_idx, cv2.CAP_V4L2)
        
        ## define codec
        self.video_writer = cv2.VideoWriter_fourcc(*self.fourcc)
        
        ## specify codec of video capture, or the default codec can't support 1080p@30fps
        ## always set codec before setting resolution to make it work
        self.cap_rec.set(cv2.CAP_PROP_FOURCC, self.video_writer)
        self.cap_rec.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_shape[0])
        self.cap_rec.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_shape[1])
        
        ## get the supported FPS the backend automatically selected (usually 30fps)
        FPS = self.cap_rec.get(cv2.CAP_PROP_FPS)
        

        while self._run_flag:
            ## start reading camera frame
            ret, cv_img = self.cap_rec.read()
            
            ## if reading time reached chunk limit
            if (time.time() > self.next_cut) and self._record_flag:
                
                ## update to next chunk limit
                self.next_cut += self.chunk_duration
                self.chunk_cnt +=1
                
                ## get the video writer for current chunk
                self.video_out = self.get_output(FPS, self.video_out)
                
            if ret: ## if successfully read a frame
                
                ## pass the image to preview
                self.preview = cv_img
                
                if self._record_flag: ## if recording
                    try:
                        self.video_out.write(cv_img)
                    except AttributeError:
                        self.video_out = cv2.VideoWriter(self.file_name, self.video_writer, FPS, self.frame_shape)
                        self.video_out.write(cv_img)
                        
                self.change_pixmap_signal.emit(cv_img)
                
        self.cap_rec.release()
        try:
            self.video_out.release()
        except AttributeError:
            pass


    def stop_record(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        if self._record_flag:
            self._record_flag = False
            
        self.should_stop = True
        
        # self.quit()