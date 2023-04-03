"""
Sample usage:

# IDs 0, 2 correspond to the cameras
c = Cameras([0, 2], "./videos/")
c.start()

import time
time.sleep(15)
c.stop_record()
"""

from vidgear.gears import VideoGear
import cv2
from threading import Thread
import mediapipe as mp
from os import path

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

W = 720
H = 480

"""
Threaded camera recorder
"""
class Cameras(Thread):
    """
    Construct a camera instance
    :param sources: Array of 2 sources for camera
    :param outpath: Folder to write video data to
    """
    def __init__(self, sources, outpath):
        Thread.__init__(self)
        self.sources = sources
        self.path = outpath
        self.should_stop = False
        self.images = []
        self.error = ""

    """
    Main loop
    """
    def run(self):
        options = {"CAP_PROP_FRAME_WIDTH": W, "CAP_PROP_FRAME_HEIGHT": H, "CAP_PROP_FPS": 30}

        fourcc = cv2.VideoWriter_fourcc('M','J','P','G')

        # OpenCV enforces some weird naming scheme so the 1 and 2 before .avi are needed
        out1, out2 = None, None
        if self.path:
            out1 = cv2.VideoWriter(path.join(self.path, 'output1.avi'), fourcc, 20.0, (W, H))
            out2 = cv2.VideoWriter(path.join(self.path, 'output2.avi'), fourcc, 20.0, (W, H))
        
        try:
            stream1 = VideoGear(source=self.sources[0], logging=True, **options).start() 
            stream2 = VideoGear(source=self.sources[1], logging=True, **options).start() 
        except RuntimeError:
            # Failed to init cameras
            if self.path:
                out1.release()
                out2.release()
            cv2.destroyAllWindows()
            self.error = "Failed to init camera (check connection or contact support)"
            return

        def parse_image(image, out):
            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = face_detection.process(image)

            # Draw the face detection annotations on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            if results.detections:
                for detection in results.detections:
                    pass
                    # mp_drawing.draw_detection(image, detection)

            if self.path:
                out.write(image.astype('uint8'))
            else:
                self.images.append(image)

        with mp_face_detection.FaceDetection(
            model_selection=0, min_detection_confidence=0.5) as face_detection:

            while True:
                self.images = self.images[-2:]
                frameA = stream1.read()
                frameB = stream2.read()

                if frameA is None or frameB is None or self.should_stop:
                    break

                parse_image(frameA, out1)
                parse_image(frameB, out2)

        if self.path:
            out1.release()
            out2.release()
        cv2.destroyAllWindows()
        stream1.stop()
        stream2.stop()

    """
    Stop recording and write to file
    """
    def stop_record(self):
        self.should_stop = True
