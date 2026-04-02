import numpy as np
from scipy import signal

class SignalProcessing:
    def __init__(self , samplerate = 48000 , carrier_frequency = 18500 , bandwidth = 300 , N = 6 , window_size = 100 , hop_size = 50):
        self.sr = samplerate 
        self.cf = carrier_frequency
        self.bandwidth = bandwidth 
        self.N = N # Filter order

        self.window_size = window_size
        self.hop_size = hop_size

        # compute filter coefficients 

        f_low = self.cf - self.bandwidth
        f_high = self.cf + self.bandwidth

        W_low = (f_low) / (self.sr / 2)
        W_high = (f_high) / (self.sr / 2)

        self.b , self.a = signal.butter(N= self.N , Wn=(W_low , W_high) , btype="bandpass")

        self.window = signal.windows.hann(self.N)

        # precompute FFT frequency bins
        self.freqs = np.fft.rfftfreq(self.N , d=1/self.sr)
        self.freq_mask = (self.freqs >= f_low) & (self.freqs <= f_high)
        self.selected_freqs = self.freqs[self.freq_mask]


    def bandpass(self , window):
        return signal.lfilter(self.b,self.a,window)

    def stft(self , window):

        # apply window function
        windowed = window * self.window

        # compute FFT

        fft_result = np.fft.rfft(windowed , n=self.N)
        magnitude = np.abs(fft_result)

        # select frequencies within the band
        magnitude = magnitude[self.freq_mask]

        #convert to dB
        magnitude = 20 * np.log10(magnitude + 1e-6) # add small value to avoid log(0)
        return magnitude

    def process_window(self , window):
        # first we need to implement the bandpass filter
        filtered_window = self.bandpass(window)
