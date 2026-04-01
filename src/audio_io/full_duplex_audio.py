import sounddevice as sd
import numpy as np
import queue # Latency problem : To be changed later to use numpy circular buffer 

class FullDuplexAudio:

    def __init__(self, sample_rate = 48000 , channels = 1 , buffer_size = 512):
        
        self.sample_rate = sample_rate # how many snapshots of sound per second
        self.channels = channels # channels we are going to use mono
        self.buffer_size = buffer_size # how many samples are processed in each callback

        self.input_queue = queue.Queue(maxsize=10)
        self.output_queue = queue.Queue(maxsize=10)
        
        self.stream = None
        self.is_running = False

        self.phase = 0.0 

    def generate_tone(self , frequency = 440.0 , duration_frames = None):
        """
        Generates audio chunks and pushes them to the output_queue.
        This should be called from a separate thread or a loop in the main thread.
        """
        if not self.is_running:
            return

        # Calculate samples needed for one buffer chunk
        # We want to match the buffer_size to keep latency low
        samples_to_generate = self.buffer_size 
        
        # Create time array for this chunk
        t = np.linspace(0, samples_to_generate / self.sample_rate, samples_to_generate)
        
        # Generate Sine Wave
        # Update phase to ensure continuity between chunks (avoid clicking)
        self.phase += 2 * np.pi * frequency * (samples_to_generate / self.sample_rate)
        self.phase %= 2 * np.pi # Keep phase manageable
        
        # Simple oscillator logic
        audio_chunk = np.sin(2 * np.pi * frequency * t + self.phase)

        self.phase += 2 * np.pi * frequency * (samples_to_generate / self.sample_rate)
        audio_chunk = np.sin(2 * np.pi * frequency * t + self.phase)
        
        # Reshape to match (frames, channels) expected by sounddevice
        audio_chunk = audio_chunk.reshape(-1, 1)

        # Put into queue (Non-blocking)
        try:
            self.output_queue.put(audio_chunk, block=False)
        except queue.Full:
            # If we are generating faster than audio plays, drop old frames
            pass

    def audio_callback(self, indata , outdata , time , frames , status):
        #check status
        if status:
            print(status)

        #copy indata into input_queue
        try:
            self.input_queue.put_nowait(indata.copy())
        except queue.Full:
            pass  # drop frame

        #fill the outdata from output_queue
        try:
            # Try to get pre-generated audio data
            audio_data = self.output_queue.get(block=False)
            
            # Ensure shapes match (safety check)
            if audio_data.shape == outdata.shape:
                outdata[:] = audio_data
            else:
                outdata.fill(0) # Safety fallback
        except queue.Empty:
            # If no data is ready, output SILENCE. 
            # NEVER wait for data in the callback.
            outdata.fill(0)

    def start(self):
        self.stream = sd.Stream(self.sample_rate , channels=self.channels , callback=self.audio_callback , latency='low' , blocksize=self.buffer_size)
        self.stream.start()
        self.is_running = True

    def stop(self):
        self.stream.stop()
        self.is_running = False

        



if __name__ == "__main__":
    audio = FullDuplexAudio()
    audio.start()

    try:
        while True:
            # Generate audio continuously (no sleep or very small sleep)
            audio.generate_tone(frequency=440)
            
            sd.sleep(1)  #Short sleep for not 100% CPU usage
            pass  # No sleep = smoothest audio
            
    except KeyboardInterrupt:
        audio.stop()