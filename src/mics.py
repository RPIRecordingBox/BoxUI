"""
Sample usage:

mics = [Microphone(*x) for x in mics]

print("Start")
mics[0].start()
mics[1].start()

import time
time.sleep(15)
mics[0].stop_record()
mics[1].stop_record()

print("Done")
p.terminate()
"""

import pyaudio
import wave
import numpy as np
from threading import Thread
from os import path
import queue

from src.audio_writer import AudioWriter
from src.config import CHUNK

"""
Threaded microphone for recording audio data
"""
class Microphone(Thread):
    """
    Construct a microphone instance
    :param i: Index of microphone
    :param sample_rate: Sample rate in hZ
    :param channels: Channels to record as int > 0
    :param folder: Folder to save output in, or None to not save
    """
    def __init__(self, i, sample_rate, channels, folder):
        Thread.__init__(self)
        self.i = i
        self.sample_rate = int(sample_rate)
        self.channels = channels
        self.file_name = path.join(folder, f"out{i}.wav") if folder else None
        self.should_stop = False
        self.to_process = queue.Queue()
        self.writer = AudioWriter(folder, self) if folder else None
        self.moving_average = []

    """
    Main loop
    """
    def run(self):
        self.generate_stream()
        self.generate_output_file()

        started = False

        while not self.should_stop:
            data = self.stream.read(CHUNK, exception_on_overflow = False)
            if self.writer != None: # Write to file
                self.wf.writeframes(data)
                self.to_process.put(data)
            else: # log moving average
                self.moving_average = [data]

            if not started and self.writer != None:
                Thread(target=self.writer.run, daemon=True).start()
                started = True

        if self.writer != None:
            self.to_process.join()
            self.writer.on_done()
            self.wf.close()

        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
            
    """
    Generate audio input stream
    """
    def generate_stream(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=CHUNK,
                input_device_index=self.i)

    """
    Create an output file to write to
    """
    def generate_output_file(self):
        if self.file_name == None:
            self.wf = None
            return

        wf = wave.open(self.file_name, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.sample_rate)
        self.wf = wf

    """
    Stop recording and write to file
    """
    def stop_record(self):
        self.should_stop = True
        

# Autodetect microphones
p = pyaudio.PyAudio()
info = p.get_host_api_info_by_index(0)
numdevices = info.get("deviceCount")

# Iterate all devices and locate the microphones
mics = []
for i in range(0, numdevices):
    device = p.get_device_info_by_host_api_device_index(0, i)
    if (device.get("maxInputChannels")) > 0:
        name = device.get("name")
        if "Avantree DG60" in name or "relacart" in name.lower():
            mics.append([i, device.get("defaultSampleRate"), device.get("maxInputChannels")])
