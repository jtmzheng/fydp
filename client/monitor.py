from sys import byteorder
from array import array
from numpy import mean, sqrt, square

import pyaudio
import time

CHUNK_SIZE = 512
FORMAT = pyaudio.paInt16
RATE = 44100


class Monitor:
    """Monitor class for monitoring audio signals and triggering
    functionality based on triggers
    """
    def __init__(self, threshold, run_count=1):
        self.callbacks = {}
        self.threshold = threshold
        self.run_count = run_count

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
        sound_rms = sqrt(mean(square(snd_data)))
        print("RMS: %d\n" % sound_rms)
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
            for cb in self.callbacks.values():
                ret = cb()
                if len(ret) < 10:
                    print 'Callback returned "%s"' % ret
                else:
                    print 'Callback returned %d size retval' % len(ret)

            # We should close the audio stream and create
            # a new one to ensure we don't look at new data
            stream.close()
        p.terminate()


def tmp_callback():
    print ("Callback!\n")
    time.sleep(1)
    print ("Resuming!\n")

if __name__ == '__main__':
    print("Starting Monitoring System!\n")
    monitor = Monitor(10000)
    monitor.add_callback('tmp_callback', tmp_callback)
    monitor.monitor()
    monitor.remove_callback('tmp_callback')
