import pyaudio
import wave
import numpy as np
import noisereduce as nr
from os import path

from config import CHUNK, GAIN, SECONDS
import speech_rec

def decode(in_data, channels):
    """
    Convert a byte stream into a 2D numpy array with 
    shape (chunk_size, channels)

    Samples are interleaved, so for a stereo stream with left channel 
    of [L0, L1, L2, ...] and right channel of [R0, R1, R2, ...], the output 
    is ordered as [L0, R0, L1, R1, ...]
    """
    result = np.fromstring(in_data, dtype=np.int16)
    chunk_length = len(result) // channels
    assert chunk_length == int(chunk_length)
    result = np.reshape(result, (chunk_length, channels))
    return result

def encode(signal):
    """
    Convert a 2D numpy array into a byte stream for PyAudio
    Signal should be a numpy array with shape (chunk_size, channels)
    """
    interleaved = signal.flatten()
    out_data = interleaved.astype(np.int16).tostring()
    return out_data


"""
Audio writer for parsing and recording audio
"""
class AudioWriter(object):
    """
    Construct a microphone instance
    :param sample_rate: Sample rate in hZ
    :param channels: Channels to record as int > 0
    :param folder: Folder to save output in
    :param microphone: Microphone object
    """
    def __init__(self, folder, microphone):
        self.sample_rate = microphone.sample_rate
        self.channels = microphone.channels
        self.file_name = path.join(folder, f"snippet-{microphone.i}-[NUMBER].wav")
        self.processed = 0
        self.count = 0
        self.mic = microphone

    """
    Main loop
    """
    def run(self):
        self.generate_output_file()
        q = self.mic.to_process
        C = round(SECONDS * (self.sample_rate / CHUNK))

        while True:
            data = q.get()
            data = self.format_audio(data)
            self.wf.writeframes(data)
            self.processed += 1

            if self.processed % C == C - 1:
                fn = self.get_current_filename()

                print("Many!!")
                self.count += 1
                self.wf.close()

                speech_rec.rec(fn)

                print("??")
                self.generate_output_file()

            q.task_done()

    """
    Remember to call this when done!
    """
    def on_done(self):
        print(self.processed, flush=True)
        self.wf.close()
            
    """
    Perform audio pre-formatting, such as
    gain adjustment. noise filtering, etc...
    """
    def format_audio(self, chunk):
        data = decode(chunk, 2)
        # data = nr.reduce_noise(y=data.T, sr=self.sample_rate)
        data = np.clip(data * GAIN, -1 * 2 ** 16 + 1, 2 ** 16 - 1) # Gain
        return encode(data)

    """
    Get the current filename based on count
    """
    def get_current_filename(self):
        self.file_name.replace("[NUMBER]", str(self.count)),

    """
    Create an output file to write to
    """
    def generate_output_file(self):
        wf = wave.open(self.get_current_filename(), 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.sample_rate)
        self.wf = wf
        
p = pyaudio.PyAudio()

