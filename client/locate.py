import numpy as np
import pandas as pd
import scipy as sp

from scipy.optimize import fsolve
from scipy import signal

import math
import peakutils

SPEED_SOUND = 300.0 # [m]
SAMPLING_FREQ = 9.6e6 # [Hz]

# Max filter window size
MED_WINDOW_SIZE = 21
WINDOW_SIZE = 5000

# Butterworth filter (manually calibrated) parameters
FREQ_1 = 250 #Hz
FREQ_2 = 350 #Hz

# Windowing for GCC-PHAT weighting function
F_MIN = 50  #Hz
F_MAX = 500 #Hz

# Number of peaks we want to window signal over
N_PEAKS = 10
PEAK_WINDOW_PREFIX = 3*36000
PEAK_WINDOW_SUFFIX = 36000

# Max delay given input (FIXME: Calculate from l)
MAX_DELAY = 18000

def apply_butter(f1, f2, fs, sig):
    """ Apply second order Butterworth filter to sig
    fs is sampling rate
    """
    sos = sp.signal.butter(
        2, (np.array([f1, f2]) / (fs / 2)), btype='bandpass', analog=False, output='sos'
    )
    sig = signal.sosfiltfilt(sos, sig)
    return sig

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

def movmax(seq, window=1):
    """Moving windowed max over seq of input window size
    """
    #assert len(seq) >= window
    return pd.DataFrame(seq).rolling(min_periods=1, window=window, center=True).max().values.T[0]

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
        return f
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
    return r_hat, theta_hat

def find_peak_window(sig, thres, min_dist, n):
    """ Crop `sig` around n peaks using a Butterworth filter to smooth peaks
    """
    # Butterworth filter (easier to get peaks)
    sig_crop = np.array(sig)
    sig_butter = normalize_signal(apply_butter(FREQ_1, FREQ_2, SAMPLING_FREQ, sig))

    # Find indexes for first N peaks over threshold
    idx = get_n_peaks(sig_butter, thres=thres, min_dist=min_dist, n=n)

    # Window the signal
    sig_butter[:(idx[0]-PEAK_WINDOW_PREFIX)] = 0
    sig_butter[(idx[-1]+PEAK_WINDOW_SUFFIX):] = 0
    sig_crop[:(idx[0]-PEAK_WINDOW_PREFIX)] = 0
    sig_crop[(idx[-1]+PEAK_WINDOW_SUFFIX):] = 0
    return sig_crop, sig_butter

def xcorr_peaks(sig1, sig2, n=N_PEAKS):
    """ Compute cross-correlation after applying a Buttersworth filter (see IPython notebook) to find
    first N peaks (crop around these peaks)
    """
    # Median filter both signals
    sig1 = signal.medfilt(sig1, MED_WINDOW_SIZE)
    sig2 = signal.medfilt(sig2, MED_WINDOW_SIZE)

    # Zero mean
    sig1 = sig1 - np.mean(sig1)
    sig2 = sig2 - np.mean(sig2)

    # Crop each signal about peaks
    sig1_cropped, _ = find_peak_window(sig1, thres=0.6, min_dist=1000, n=n)
    sig2_cropped, _ = find_peak_window(sig2, thres=0.6, min_dist=1000, n=n)

    # Compute xcorr of the cropped signals
    return gcc_xcorr(sig1_cropped, sig2_cropped, F_MIN, F_MAX, SAMPLING_FREQ)

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

def gcc_xcorr(sig1, sig2, fmin, fmax, fs):
    """ GCC-PHAT windowed on [fmin, fmax]
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
    corr[np.where(np.abs(samples) > MAX_DELAY)] = 0

    ind = np.argmax(corr)
    delay = -samples[ind]
    return corr, delay

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
