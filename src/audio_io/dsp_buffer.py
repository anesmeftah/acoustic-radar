import numpy as np
from collections import deque

from audio_io.full_duplex_audio import FullDuplexAudio


class SlidingWindowBuffer:
    def __init__(self , window_size = 100 , overlap = 0.5 , Hop_size = 50 , chunk_size = 512):
        self.window_size = window_size #4800 samples
        self.hop_size = Hop_size
        self.buffer_size = 2 * self.window_size
        self.chunk_size = chunk_size
        self.filled_samples = 0

        self.buffer = np.zeros((self.buffer_size , 1))
        self.window = np.zeros((self.window_size , 1))
        # maintain a writer pointer
        self.write_ptr = self.window_size # later update it with : (write_ptr + chunk_size) % Buffer_size


    def write_ptr_update(self):
        self.write_ptr = (self.write_ptr + self.chunk_size) % self.buffer_size

    def extract_window(self):
        if self.filled_samples >= self.window_size:
            self.window = self.buffer[self.write_ptr - self.window_size : self.write_ptr]
        else:
            return








