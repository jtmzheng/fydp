import sys
import socket
import math
import struct
import time
import getopt
import errno
import numpy as np

import locate
import farwave
import db

from socket import error as socket_error
from multiprocessing import Pool

from monitor import Monitor

MAX_CHUNK_SIZE = 4096
DEFAULT_HOSTNAME = '192.168.7.2'
DEFAULT_HOSTNAME_2 = '192.168.8.2'
#DEFAULT_HOSTNAME = 'localhost'
DEFAULT_PORT = 5555

# Maps angle from microphone local coordinates to array coordinates (rotation to mic 0 axis)
ANGLE_OFFSET = {
    0: 0,
    1: 2.0944, # 120 deg in rad
    2: 4.18879, # 240 deg in rad
}

# Maps each microphone to the index of left and right microphones relative to it
MIC_IND_LR = {
    0: (1, 2),
    1: (2, 0),
    2: (0, 1)
}


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
    def __init__(self, host, port, x, y, l, samples=0):
        """Given (host, port) Beaglebone is writing to
        setup connection"""
        self.host = host
        self.port = port
        self.x = x
        self.y = y
        self.l = l
        self.samples = samples*3 # 3 readings from 3 mics per sample

    def __call__(self):
        return self.read()

    def read(self):
        """Read n samples from server (0 means all)
        """
        sock = connect(self.host, self.port)
        buf = read_buffer(sock, self.samples)
        assert(buf.shape[0] % 3 == 0)

        data = buf.reshape((3, buf.shape[0]/3), order='F')
        print 'Finished reading data from socket'
        return data


class MultiBeagleReader:
    """Reads data from Beaglebones
    """
    def __init__(self, readers, x, y, timeout=100, comment=''):
        self.readers = readers
        self.timeout = timeout
        self.src_x = x
        self.src_y = y
        self.comment = comment

    def read(self):
        pool = Pool(processes=min(len(self.readers)+4, 4))

        # Fetch the data from Beaglebones asynchronously to ensure ~ temporally consistent
        results = [pool.apply_async(reader, ()) for reader in self.readers]
        bufs = [res.get(timeout=self.timeout) for res in results]

        # NB: Write data to db, order of arrays/mics is arbitrary
        exp_id = db.create_experiment(self.src_x, self.src_y, self.comment)

        angles = []
        for i in range(len(bufs)):
            buf = bufs[i]

            # sqlite only supports synchronous updates
            for j in range(len(buf)):
                mic_id = db.create_mic(exp_id, i, mic_id=j, data=buf[j])

            buf_crop, _, offsets, _ = locate.crop_sigs_npeaks(buf)
            # Asynchronously calculate xcorr for each mic to baseline mic
            results = []
            for j in range(len(buf)):
                for k in range(j, len(buf)):
                    if j != k:
                        # Map (j, k) microphone pair to xcorr task
                        results.append((
                            (j, k), pool.apply_async(locate.xcorr_peaks, args=(buf_crop[j], buf_crop[k], offsets[j], offsets[k], self.readers[i].l))
                        ))


            # 3x3 array delays[i][j] is the delay of signal j relative to signal i
            delays = np.zeros((len(buf), len(buf)), dtype=np.float)
            for res in results:
                key, val = res[0], res[1]
                delays[key[0]][key[1]] = val.get(timeout=self.timeout)[1] # xcorr (val, delay) tuple
                delays[key[1]][key[0]] = -delays[key[0]][key[1]]

            print '------- Delay Matrix -------'
            print delays
            assert len(buf) == 3 # We make some assumptions here that len(buf) == 3

            farwave_ang = np.deg2rad(farwave.calc_angle(delays, self.readers[i].l))
            angles.append(farwave_ang) # Store in radians
            print("Far Wave Angle: %r rad\n" % farwave_ang)

            # Estimate "location" of sound source, create array record
            for j in range(len(buf)):
                if delays[j][(j+1)%3] >= 0 and delays[j][(j+2)%3] >= 0:
                    lr = MIC_IND_LR[j]
                    print 'Using microphone %d as closest mic - (%d left, %d right)\n' % (j, lr[0], lr[1])
                    r, theta = locate.locate(delays[j][lr[0]], delays[j][lr[1]], self.readers[i].l)
                    arr_id = db.create_array(
                        exp_id, i, self.readers[i].x, self.readers[i].y, r, farwave_ang #theta + ANGLE_OFFSET[j]
                    )
                    break

            # Write each mic pair to db (NB: Redundant data but small size so okay)
            for j in range(len(buf)):
                for k in range(len(buf)):
                    db.create_mic_pair(exp_id, i, j, k, delays[j][k])

        # Clean up
        pool.close()
        pool.join()

        # Calc estimated position and store in db
        assert len(bufs) == 2
        pos = locate.calc_poi(
            np.array([self.readers[0].x, self.readers[0].y]),
            np.array([self.readers[1].x, self.readers[1].y]),
            np.array([np.sin(angles[0]), np.cos(angles[0])]),
            np.array([np.sin(angles[1]), np.cos(angles[1])])
        )
        print 'Estimated position: %f, %f' % (pos[0], pos[1])
        db.set_pos_estimate(exp_id, pos[0], pos[1])
        return bufs

def run(argv):
    """Main entry point of client
    """
    portno = DEFAULT_PORT
    hostname = DEFAULT_HOSTNAME
    hostname_2 = DEFAULT_HOSTNAME_2

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
            elif opt in ("-h2", "--hostname2"):
                print ('Hostname 2: %s' % arg)
                hostname_2 = arg
    except getopt.GetoptError:
        print 'client.py -h <hostname> -h2 <hostname_2> -p <port>'
        print 'Using default host localhost and default port 5555'


    # Parse user input (TODO: Some sort of config file?)
    print 'Enter sound source location (origin by default):'
    src_x = float(raw_input('x: ') or '0')
    src_y = float(raw_input('y: ') or '0')
    print 'Enter array 1 position:'
    x1 = float(raw_input('x: '))
    y1 = float(raw_input('y: '))
    print 'Enter array 2 position'
    x2 = float(raw_input('x: '))
    y2 = float(raw_input('y: '))
    print 'Enter array 1 length:'
    l1 = float(raw_input('l: '))
    print 'Enter array 2 length (Same as array 1 by default):'
    l2 = float(raw_input('l: ') or l1)
    print 'Enter number of runs (Default 1)'
    runs = int((raw_input('Runs: ') or '1'))
    print 'Enter experiment descriptor (Optional)'
    comment = raw_input('Comment: ') or ''

    m = Monitor(300, runs)

    # NB: Use same port for both hosts
    br_1 = BeagleReader(hostname, portno, x=x1, y=y1, l=l1, samples=0)
    br_2 = BeagleReader(hostname_2, portno, x=x2, y=y2, l=l2, samples=0)

    # NB: Enable below to test locally with test local server(s) running
    #br_1 = BeagleReader('localhost', 5555, x=x1, y=y1, l=l1, samples=0)
    #br_2 = BeagleReader('localhost', 5556, x=x2, y=y2, l=l2, samples=0)

    # NB: We want the whatever reader/consumer to write out structured data
    # to persistent storage (ie with metadata, raw data, analysis, etc)
    mbr = MultiBeagleReader([br_1, br_2], src_x, src_y, 100, comment)

    m.add_callback('[MultiBeagleReader::read]', mbr.read)
    m.monitor()
    return
