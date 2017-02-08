import sys
import socket
import math
import struct
import time
import getopt
import errno
import numpy as np

import locate
import db

from socket import error as socket_error
from multiprocessing import Pool

from monitor import Monitor

MAX_CHUNK_SIZE = 4096
DEFAULT_HOSTNAME = 'localhost'
DEFAULT_PORT = 5555


def read_data(sock, nbytes):
    """Read nbytes of data from socket
    """
    buf = ''
    while nbytes > 0:
        chunk_size = min(MAX_CHUNK_SIZE, nbytes)
        data = sock.recv(chunk_size)
        if not data:
            return None
        buf += data
        # Subtract out the number of bytes actually read
        # NB: It actually doesn't really make a difference
        # if we decide to use socket.MSG_WAITALL...
        nbytes -= len(data)
    output = np.fromstring(buf, dtype=np.uint8)
    return output

def write_req(sock, nsamples):
    """Write request for n-samples of data to be written
    to socket by server
    """
    nsamples = socket.htonl(nsamples)
    sock.sendall(struct.pack("I", nsamples))
    return

def read_int(sock):
    """Read a single 4 byte integer from socket
    """
    raw = sock.recv(4, socket.MSG_WAITALL)
    if raw == None:
        return None
    return socket.ntohl(struct.unpack('I', raw)[0])

def read_buffer(sock, nsamples=0):
    """Read buffer with n samples of data from socket
    """
    write_req(sock, nsamples)
    nsamples = read_int(sock)
    print 'Reading %d samples' % nsamples
    buf = read_data(sock, nsamples)
    return buf

def connect(host, port):
    """Tries to connect until timeout (if specified)
    and returns socket
    """
    # NB: Creating socket and connecting can both throw errors,
    # we just want to fail fast in those cases (for now)
    host = socket.gethostbyname(host)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Currently just retry
    connected = False
    while not connected:
        try:
            s.connect((host, port))
            connected = True
        except socket_error as serr:
            if serr.errno != errno.ECONNREFUSED:
                # Re-raise if not ECONNREFUSED
                raise serr
            print 'Connection refused, retry in 1 s'
            time.sleep(1)
    return s

class BeagleReader:
    """Reads data from Beaglebone
    """
    def __init__(self, host, port, x, y, samples=0):
        """Given (host, port) Beaglebone is writing to
        setup connection"""
        self.host = host
        self.port = port
        self.x = x
        self.y = y
        self.samples = samples*3 # 3 readings from 3 mics per sample

    def __call__(self):
        return self.read()

    def read(self):
        """Read n samples from server (0 means all)
        """
        sock = connect(self.host, self.port)
        buf = read_buffer(sock, self.samples)
        assert(buf.shape[0] % 3 == 0)

        data = buf.reshape(3, buf.shape[0]/3)
        print 'Finished reading data from socket'
        return data


class MultiBeagleReader:
    """Reads data from Beaglebones
    """
    def __init__(self, readers, x, y, timeout=10):
        self.readers = readers
        self.timeout = timeout
        self.src_x = x
        self.src_y = y

    def read(self):
        pool = Pool(processes=min(len(self.readers)+4, 4))
        results = [pool.apply_async(reader, ()) for reader in self.readers]
        bufs = [res.get(timeout=self.timeout) for res in results]

        # Clean up
        pool.close()
        pool.join()

        # NB: Write data to db, order of arrays/mics is arbitrary
        exp_id = db.create_experiment(self.src_x, self.src_y)
        for i in range(len(bufs)):
            arr_id = db.create_array(exp_id, i, self.readers[i].x, self.readers[i].y)
            buf = bufs[i]
            mic_id = db.create_mic(exp_id, i, mic_id=0, data=','.join(str(v) for v in buf[0]), delay=0)
            for j in range(1, len(bufs[i])):
                # For now use first signal as baseline (may have negative delay, which is fine)
                _, delay = locate.xcorr(buf[0], buf[j])
                mic_id = db.create_mic(exp_id, i, mic_id=j, data=','.join(str(v) for v in buf[j]), delay=delay)

        return bufs

def main(argv):
    """Main entry point of client
    """
    portno = DEFAULT_PORT
    hostname = DEFAULT_HOSTNAME

    try:
        opts, args = getopt.getopt(argv, 'h:p:',['hostname=', 'port='])
        for opt, arg in opts:
            if opt == '--help':
                print 'client.py -h <hostname> -p <port>'
                sys.exit(0)
            elif opt in ('-p', '--port'):
                print ('Port: %s' % arg)
                portno = int(arg)
            elif opt in ("-h", "--hostname"):
                print ('Hostname: %s' % arg)
                hostname = arg
    except getopt.GetoptError:
        print 'client.py -h <hostname> -p <port>'
        print 'Using default host localhost and default port 5555'


    # Parse user input (TODO: Some sort of config file?)
    print 'Enter sound source location:'
    src_x = float(raw_input('x: '))
    src_y = float(raw_input('y: '))
    print 'Enter array 1 position:'
    x1 = float(raw_input('x: '))
    y1 = float(raw_input('y: '))

    m = Monitor(3000)

    # NB: For testing I ran a second local server on port 5556
    # TODO: Use different hosts/ports
    br_1 = BeagleReader(hostname, portno, x=x1, y=y1, samples=0)
    # br_2 = BeagleReader(hostname, 5556, 0, 0, 30)

    # NB: We want the whatever reader/consumer to write out structured data
    # to persistent storage (ie with metadata, raw data, analysis, etc)
    mbr = MultiBeagleReader([br_1,], src_x, src_y)

    m.add_callback('[MultiBeagleReader::read]', mbr.read)
    m.monitor()
    return

if __name__ == '__main__':
    main(sys.argv[1:])
