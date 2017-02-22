import numpy as np
import pandas as pd
import scipy as sp

from scipy.optimize import fsolve
from scipy import signal

import math

SPEED_SOUND = 300.0 # [m]
SAMPLING_FREQ = 9500000.0 # [Hz]

# Max filter window size
MED_WINDOW_SIZE = 21
WINDOW_SIZE = 5000

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

def xcorr(sig1, sig2):
    """ Cross-correlation (NB: http://stackoverflow.com/questions/12323959/fast-cross-correlation-method-in-python)
    """
    sig1 = signal.medfilt(sig1, MED_WINDOW_SIZE)
    sig2 = signal.medfilt(sig2, MED_WINDOW_SIZE)

    n = len(sig1)
    sig1 = np.abs(sig1 - np.mean(sig1))
    sig2 = np.abs(sig2 - np.mean(sig2))

    sig1 = movmax(sig1, WINDOW_SIZE)
    sig2 = movmax(sig2, WINDOW_SIZE)

    # NB: This matches MATLAB's xcorr functionality
    corr = np.abs(signal.fftconvolve(sig1, sig2[::-1], mode='full'))

    arg_max = np.argmax(corr)
    ind = arg_max - (n-1)

    max_corr = corr[arg_max]

    # Negative `ind` since we want how much sig2 should be shifted to maximize correlation with sig1
    return max_corr, -ind


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
