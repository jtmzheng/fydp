from sys import byteorder
from array import array
from numpy import mean, sqrt, square
from scipy import signal
import numpy as np
import scipy as sp

import pyaudio
import time

CHUNK_SIZE = 512
FORMAT = pyaudio.paInt16
RATE = 44100


class Monitor:
    """Monitor class for monitoring audio signals and triggering
    functionality based on triggers
    """
    def __init__(self, threshold, run_count=1, freq=(200, 350)):
        self.callbacks = {}
        self.threshold = threshold
        self.run_count = run_count
        self.max_val = 0

        if freq is not None:
            self.sos_filter = sp.signal.butter(2, (np.array(freq) / (float(RATE) / 2)),
                            btype='bandpass', analog=False, output='sos')
        else:
            self.sos_filter = None

    def add_callback(self, name, cb):
        """Add a callback to respond to triggers from monitor
        """
        if name in self.callbacks:
            raise NameError('Callback with name %s already exists' % name)
        self.callbacks[name] = cb

    def remove_callback(self, name):
        """Removes callback by name
        """
        del self.callbacks[name]

    def is_silent(self, snd_data):
        """Returns true if below the 'silent' threshold
        """
        if self.sos_filter is not None:
            sound_rms = sqrt(mean(square(signal.sosfiltfilt(self.sos_filter, np.array(snd_data)))))
        else:
            sound_rms = sqrt(mean(square(snd_data)))


        self.max_val = max(self.max_val, sound_rms)
        print("RMS: %d, prev_max: %d\n" % (sound_rms, self.max_val))
        return sound_rms < self.threshold

    def monitor(self):
        """Start monitoring loop
        NB: We close the old audio stream and create a new one each time
        we capture noise to ensure we don't process stale data that was
        left in the old stream
        """

        p = pyaudio.PyAudio()
        while self.run_count > 0:
            self.run_count -= 1
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

                silent = self.is_silent(snd_data)

            stream.stop_stream()
            time.sleep(0.01)
            self.max_val = 0
            for cb in self.callbacks.values():
                print 'Calling monitor callback...'
                ret = cb()
                print 'Callback returned %r size retval' % ret

            # We should close the audio stream and create
            # a new one to ensure we don't look at new data
            stream.close()
        p.terminate()

        return ret


def tmp_callback():
    print ("Callback!\n")
    time.sleep(1)
    print ("Resuming!\n")
    return []

if __name__ == '__main__':
    print("Starting Monitoring System!\n")
    monitor = Monitor(350)
    monitor.add_callback('tmp_callback', tmp_callback)
    monitor.monitor()
    monitor.remove_callback('tmp_callback')
