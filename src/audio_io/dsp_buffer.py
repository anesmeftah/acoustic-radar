import numpy as np
from collections import deque

from audio_io.full_duplex_audio import FullDuplexAudio


class SlidingWindowBuffer:
    def __init__(self , window_size = 100 , overlap = 0.5 , Hop_size = 50 , chunk_size = 512 , channels = 1):
        self.window_size = window_size #4800 samples
        self.hop_size = Hop_size
        self.buffer_size = 2 * self.window_size
        self.channels = channels

        self.filled_samples = 0

        self.buffer = np.zeros((self.buffer_size , self.channels))
        #self.window = np.zeros((self.window_size , self.channels))
        # maintain a writer pointer
        self.write_ptr = 0 # later update it with : (write_ptr + chunk_size) % Buffer_size
        self.new_samples_since_last_window = 0 # this is the hop counter

    # write incoming samples
    def write(self , samples):
        num_samples = samples.shape[0]

        end_ptr = self.write_ptr + num_samples

        # Case 1 : no need to divide
        if end_ptr <= self.buffer_size:
            self.buffer[self.write_ptr : end_ptr] = samples
        else:
            # Case 2 : we need to divide
            first_part = self.buffer_size - self.write_ptr
            self.buffer[self.write_ptr:] = samples[:first_part]
            self.buffer[:end_ptr % self.buffer_size] = samples[first_part:]

        #update write pointer
        self.write_ptr = end_ptr % self.buffer_size

        #update counters
        self.filled_samples = min(self.buffer_size, self.filled_samples + num_samples)
        self.new_samples_since_last_window += num_samples

    #check if the window is ready
    def is_ready(self):
        return (
            self.filled_samples >= self.window_size and self.new_samples_since_last_window >= self.hop_size
        )




    def extract_window(self):

        if not self.is_ready():
            return None
        
        start = (self.write_ptr - self.window_size) % self.buffer_size

        # Case 1
        if start < self.write_ptr:
            window = self.buffer[start:self.write_ptr]
        else: #Case 2
            window = np.vstack((
                self.buffer[start:],
                self.buffer[:self.write_ptr]
            ))
        
        #update hop counter
        self.new_samples_since_last_window -= max(0,self.hop_size)

        return window









