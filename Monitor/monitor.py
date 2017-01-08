from sys import byteorder
from array import array
from numpy import mean, sqrt, square

import pyaudio
import time

THRESHOLD = 10000
CHUNK_SIZE = 512
FORMAT = pyaudio.paInt16
RATE = 44100

def is_silent(snd_data):
    # Returns 'True' if below the 'silent' threshold
    sound_rms = sqrt(mean(square(snd_data)))
    print("RMS: %d\n" % sound_rms)
    return sound_rms < THRESHOLD

def tmp_callback():
    print ("Callback!\n")
    time.sleep(1)
    print ("Resuming!\n")

def monitor_sound(callback):

    # Go to Infinite Monitoring Loop
    # Note: We create a new audio stream
    # every time so that 
    p = pyaudio.PyAudio()
    
    while 1:
        stream = p.open(format=FORMAT, channels=1, rate=RATE,
                        input=True, output=True,
                        frames_per_buffer=CHUNK_SIZE)

        # little endian, signed short
        snd_data = array('h', stream.read(CHUNK_SIZE))
        if byteorder == 'big':
            snd_data.byteswap()

        silent = is_silent(snd_data)

        if not silent:
            callback()

        # We should close the audio
        # stream so the next time
        sample_width = p.get_sample_size(FORMAT)
        stream.stop_stream()
        stream.close()
    p.terminate()


if __name__ == '__main__':
    print("Starting Monitoring System!\n")
    monitor_sound(tmp_callback)