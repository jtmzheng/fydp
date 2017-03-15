import numpy as np
import pandas as pd
import scipy as sp

from scipy.optimize import fsolve, root, least_squares
from scipy import signal

import math
import peakutils

SPEED_SOUND = 340.0 # [m/s]
SAMPLING_FREQ = 9.5e6 # [Hz]

# Max filter window size
MED_WINDOW_SIZE = 21
WINDOW_SIZE = 5000

# Butterworth filter (manually calibrated) parameters
FREQ_1 = 262-75 #Hz
FREQ_2 = 262+75 #Hz

# Number of peaks we want to window signal over
N_PEAKS = 5
PEAK_WINDOW_PREFIX = 2*36000
PEAK_WINDOW_SUFFIX = 0*36000

MIN_PEAK_DIST = 26000
MAX_PEAK_DIST = 46000
PEAK_THRESH_HIGH = 0.15
PEAK_THRESH_LOW = 0.01

def apply_butter(f1, f2, fs, sig):
    """ Apply second order Butterworth filter to sig
    fs is sampling rate
    """
    sos = sp.signal.butter(
        2, (np.array([f1, f2]) / (fs / 2)), btype='bandpass', analog=False, output='sos'
    )
    sig_butter = signal.sosfiltfilt(sos, sig)
    return sig_butter

def normalize_signal(sig):
    """ Normalize signal and zero-mean
    """
    sig = (sig - np.min(sig)) / (np.max(sig) - np.min(sig))
    return sig - np.mean(sig)

def get_n_peaks(sig, thres, min_dist, n):
    """ Gets the first n peaks > thres ([0, 1]) and greater than min_dist apart
    """
    idx = peakutils.peak.indexes(sig, thres=thres, min_dist=min_dist)

    return idx[:n]

def movmax(seq, window=MED_WINDOW_SIZE):
    """Moving windowed max over seq of input window size
    """
    #assert len(seq) >= window
    return pd.DataFrame(seq).rolling(min_periods=1, window=window, center=True).max().values.T[0]

def median_filter(seq, window=1):
    """Moving windowed median over seq of input window size
    """
    #assert len(seq) >= window
    return pd.DataFrame(seq).rolling(min_periods=1, window=window, center=True).median().values.T[0]

def find_nearest(array,value):
    idx = (np.abs(array-value)).argmin()
    return array[idx]

def calc_rel_delay(r, theta, l):
    """Generate ideal relative delay (f1, f2) given (r, theta) and l
    """
    f1 = (
        math.sqrt(r*r + l*l - 2*l*r*math.cos(2*math.pi/3 + theta)) -
        math.sqrt(r*r + l*l - 2*l*r*math.cos(theta))
    )
    f2 = (
        math.sqrt(r*r + l*l - 2*l*r*math.cos(2*math.pi/3 - theta)) -
        math.sqrt(r*r + l*l - 2*l*r*math.cos(theta))
    )
    return (f1/SPEED_SOUND, f2/SPEED_SOUND)

def generate_delay_func(f1, f2, l):
    """Given parameters f1, f2, l (relative delays + length between microphones)
    return closure to solve for (r, theta)
    """
    def delay_func(x):
        r, theta = x[0], x[1]
        f = [
            math.sqrt(r*r + l*l - 2*l*r*math.cos(2*math.pi/3 + theta)) -
            math.sqrt(r*r + l*l - 2*l*r*math.cos(theta)) -
            f1*SPEED_SOUND,
        ]
        f.append(
            math.sqrt(r*r + l*l - 2*l*r*math.cos(2*math.pi/3 - theta)) -
            math.sqrt(r*r + l*l - 2*l*r*math.cos(theta)) -
            f2*SPEED_SOUND
        )
        return np.array(f)
    return delay_func

def locate(f1, f2, l, r0=5, theta0=(math.pi/6)):
    """Locate position given relative delays f1, f2 (in # of samples)
    NB: Order of f1, f2 doesn't matter here, but determines which axis
    theta is relative to
    """
    # Convert delay to time delay (samples/sampling freq)
    f1 = float(f1) / SAMPLING_FREQ
    f2 = float(f1) / SAMPLING_FREQ
    func = generate_delay_func(f1, f2, l)
    r_hat, theta_hat = fsolve(func, [r0, theta0])
    #sol = root(func, [r0, theta0], method='lm')
    #sol = least_squares(func, x0=(r0, theta0), method='trf', bounds=([2., -np.pi/3], [10, np.pi/3]))
    #print 'Optimizer message: %s' % sol.message
    #r_hat, theta_hat = sol.x[0], sol.x[1]
    return r_hat, theta_hat

def find_peak_window(sig, thres, min_dist, n, closest_to=None):
    """ Crop `sig` around n peaks using a Butterworth filter to smooth peaks
    """
    # Butterworth filter (easier to get peaks)
    sig = np.array(sig) # Copy so we don't modify the input when truncating
    sig_butter = normalize_signal(apply_butter(FREQ_1, FREQ_2, SAMPLING_FREQ, sig))
    idx = get_n_peaks(sig_butter, thres=thres, min_dist=min_dist, n=n)

    # Window the signal
    if closest_to is None:
        # Find indexes for first N peaks over threshold
        offset_low = (idx[0]-PEAK_WINDOW_PREFIX)
        offset_high = (idx[-1]+PEAK_WINDOW_SUFFIX)
        pk_locs = (idx[0], idx[-1])

    else:
        # NB: No codepath to this yet
        pk_locs = (find_nearest(idx,closest_to[0]), find_nearest(idx,closest_to[1]))
        offset_low = (pk_locs[0]-PEAK_WINDOW_PREFIX)
        offset_high = (pk_locs[-1]+PEAK_WINDOW_SUFFIX)

    sig_butter = sig_butter[offset_low:offset_high]
    sig = sig[offset_low:offset_high]
    return sig, sig_butter, offset_low, pk_locs

def calc_max_delay(l):
    """ Compute the max delay possible given microphone center distance l
    """
    return l*math.sqrt(3)*SAMPLING_FREQ/SPEED_SOUND


def xcorr_peaks(sig1, sig2, offset1, offset2, l):
    """ Compute cross-correlation after applying a Buttersworth filter (see IPython notebook) to find
    first N peaks (crop around these peaks)
    """
    # Median filter both signals
    sig1 = median_filter(sig1, MED_WINDOW_SIZE)
    sig2 = median_filter(sig2, MED_WINDOW_SIZE)

    # Zero mean
    sig1 = sig1 - np.mean(sig1)
    sig2 = sig2 - np.mean(sig2)

    # Crop each signal about peaks
    max_delay = calc_max_delay(l)
    # Compute xcorr of the cropped signals
    corr, delay = gcc_xcorr(sig1, sig2, max_delay, -(offset2 - offset1), FREQ_1, FREQ_2, SAMPLING_FREQ)
    return corr, (delay + (offset2 - offset1))

def find_first_peak(sig, peak_thresh_high, peak_thresh_low):
    """ Finds the first peak that has N_PEAKS consecutive peaks
    following it at the correct distance apart
    """
    idx_peak_all = peakutils.peak.indexes(sig, thres=0, min_dist=MIN_PEAK_DIST)
    idx_peak = np.array([i for i in idx_peak_all if sig[i] >= peak_thresh_high])
    idx_peak_low = np.array([i for i in idx_peak_all if sig[i] >= peak_thresh_low])
    found = False
    first_peak = 0
    while not found:
        if (first_peak > (len(idx_peak) - N_PEAKS - 1)):
            # Here we assume signal to noise ratio for this
            # microphone is too low. So return NaN
            return float('nan'), idx_peak_low

        found = True
        for i in range(N_PEAKS):
            if (idx_peak[first_peak+i+1] - idx_peak[first_peak+i]) > MAX_PEAK_DIST:
                first_peak += 1
                found = False
                break;

    return idx_peak[first_peak], idx_peak_low

def crop_sigs(bufs):
    """ Given N signals, crop all N at the "first peak" detected for all signals
    This is done by finding the "first peak" for each signal.
    The "reference peak" is the earliest "first peak"
    Then, we crop each signal at their respective peaks that is closest to the
    reference peak
    """
    pks = []
    locations = []
    """
    sigs_butter_cropped, sigs_cropped = [], []
    offsets = []

    for i in range(len(bufs)):
        sig_cropped, sig_butter, offset, _ = find_peak_window(bufs[i], thres=0.6, min_dist=1000, n=N_PEAKS)
        sigs_butter_cropped.append(sig_butter)
        sigs_cropped.append(sig_cropped)
        offsets.append(offset)
    """

    sigs_butter, sigs = [], []
    for i in range(len(bufs)):
        sigs.append(np.array(bufs[i]))
        sigs_butter.append(normalize_signal(apply_butter(FREQ_1, FREQ_2, SAMPLING_FREQ, sigs[i])))
        pk, locs = find_first_peak(sigs_butter[i], PEAK_THRESH_HIGH, PEAK_THRESH_LOW)
        pks.append(pk)
        locations.append(locs)

    pk_ref = np.nanmin(pks)
    if np.isnan(pk_ref):
        raise RuntimeError("Could not find a reference peak")

    offsets = []
    sigs_cropped, sigs_butter_cropped = [], []
    for i in range(len(bufs)):
        pk_ref_i = find_nearest(locations[i], pk_ref)
        offset_i = (pk_ref_i-PEAK_WINDOW_PREFIX)
        offsets.append(pk_ref_i)
        sigs_butter_cropped.append(sigs_butter[i][offset_i:pk_ref_i+PEAK_WINDOW_SUFFIX])
        sigs_cropped.append(sigs[i][offset_i:pk_ref_i+PEAK_WINDOW_SUFFIX])

    return sigs_cropped, sigs_butter_cropped, offsets

def xcorr(sig1, sig2):
    """ Cross-correlation (NB: http://stackoverflow.com/questions/12323959/fast-cross-correlation-method-in-python)
    """
    n = len(sig1)
    sig1 = (sig1 - np.mean(sig1))
    sig2 = (sig2 - np.mean(sig2))

    sig1 = movmax(sig1, WINDOW_SIZE)
    sig2 = movmax(sig2, WINDOW_SIZE)

    # NB: This matches MATLAB's xcorr functionality
    corr = np.abs(signal.fftconvolve(sig1, sig2[::-1], mode='full'))

    arg_max = np.argmax(corr)
    ind = arg_max - (n-1)

    max_corr = corr[arg_max]

    # Negative `ind` since we want how much sig2 should be shifted to maximize correlation with sig1
    return max_corr, -ind

def next_pow_2(n):
    """ Much faster to fft at next pow of 2
    """
    return np.power(2, np.ceil(np.log2(n)))

def gcc_xcorr(sig1, sig2, max_delay, offset, fmin, fmax, fs):
    """ GCC-PHAT windowed on [fmin, fmax]

    offset: difference in truncation difference in start for sig1, sig2
    """
    Nfft = int(next_pow_2(len(sig1) + len(sig2) - 1))

    SIG1 = np.fft.fftshift(np.fft.fft(sig1, n=Nfft))
    SIG2 = np.fft.fftshift(np.fft.fft(sig2, n=Nfft))
    freq = np.fft.fftshift(np.fft.fftfreq(n=Nfft, d=1./fs))

    CORR = np.multiply(SIG1, np.conj(SIG2))
    CORR[np.where(np.abs(freq) < fmin)] = 0 # window in frequency domain
    CORR[np.where(np.abs(freq) > fmax)] = 0

    CORR = CORR / (np.abs(SIG1) * np.abs(np.conj(SIG2)))
    corr = np.fft.ifft(np.fft.ifftshift(CORR))
    corr = np.fft.fftshift(corr)

    # Crop out anything > MAX_DELAY (This is a kludge to ensure max correlation is within
    # physically possible limits
    samples = np.arange(len(corr))
    samples -= len(samples)/2
    corr[np.where(np.abs(samples + offset) > max_delay)] = 0

    ind = np.argmax(corr)
    delay = -samples[ind]

    return (samples, corr), delay

def calc_poi(p1, p2, v1, v2):
    """ Calculate POI of two rays (p1 + t*v1) and (p2 + t*v2)
    NB: Assume all inputs are ndarrays
    """
    par = np.dot(np.linalg.pinv(np.array([[v1[0], -v2[0]], [v1[1], -v2[1]]])), p2 - p1)
    return p1 + par[0] * v1; # Equivalent to p2 + par[1]*v2

if __name__ == '__main__':
    # Test position
    r = 2 # [m]
    theta = 15 # [deg]

    # Constants
    l = 0.3;                # distance between microphones
    err = 0.00002 * SPEED_SOUND;
    f1, f2 = calc_rel_delay(r, math.radians(theta), l);
    r_hat, theta_hat = locate(f1 + err, f2 + err, l)

    print 'Rhat = %f, ThetaHat = %f' % (r_hat, math.degrees(theta_hat))
