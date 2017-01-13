import sys
import socket
import math
import struct
import time
import getopt

import errno
from socket import error as socket_error

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

    output = []
    for i in range(0, len(buf)):
        c = struct.unpack('c', buf[i])
        output.append(ord(c[0]))

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

def deinterleave(buf):
    assert len(buf) % 3 == 0
    data = [[], [], []]
    for i in range(0, len(buf), 3):
        data[0].append(buf[i])
        data[1].append(buf[i+1])
        data[2].append(buf[i+2])
    return data

class BeagleReader:
    """Reads data from Beaglebone
    """
    def __init__(self, host, port, samples=0):
        """Given (host, port) Beaglebone is writing to
        setup connection"""
        self.host = host
        self.port = port
        self.samples = samples

    def read(self):
        """Read n samples from server (0 means all)
        """
        sock = connect(self.host, self.port)
        buf = read_buffer(sock, self.samples)
        data = deinterleave(buf)
        return data


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

    m = Monitor(3000)
    br = BeagleReader(hostname, portno, 9)
    m.add_callback('[BeagleReader::read]', br.read)
    m.monitor()
    return

if __name__ == '__main__':
    main(sys.argv[1:])
