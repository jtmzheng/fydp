from sys import byteorder
from array import array
from numpy import mean, sqrt, square

import pyaudio
import time

CHUNK_SIZE = 512
FORMAT = pyaudio.paInt16
RATE = 44100

def is_silent(snd_data, threshold):
    """Returns 'True' if below the 'silent' threshold"""
    sound_rms = sqrt(mean(square(snd_data)))
    print("RMS: %d\n" % sound_rms)
    return sound_rms < threshold

def tmp_callback():
    print ("Callback!\n")
    time.sleep(1)
    print ("Resuming!\n")

def monitor_sound(callback_list, threshold):
    """
    Go to Infinite Monitoring Loop
    Note: We close the old audio stream and create a new one each time
    we capture noise to ensure we don't process stale data that was left in the
    old stream
    """

    p = pyaudio.PyAudio()
    
    while 1:
        stream = p.open(format=FORMAT, channels=1, rate=RATE,
                        input=True, output=True,
                        frames_per_buffer=CHUNK_SIZE)

        silent = True

        # Keep polling until silent
        while (silent):
            # little endian, signed short
            snd_data = array('h', stream.read(CHUNK_SIZE))
            if byteorder == 'big':
                snd_data.byteswap()

            silent = is_silent(snd_data, threshold)

        stream.stop_stream()
        for callback in callback_list:
            callback()

        # We should close the audio stream and create
        # a new one to ensure we don't look at new data
        stream.close()
    p.terminate()


if __name__ == '__main__':
    print("Starting Monitoring System!\n")
    monitor_sound([tmp_callback], 10000)