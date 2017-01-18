import numpy as np

from scipy.optimize import fsolve

import math

SPEED_SOUND = 300 # [m]

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
    return (f1, f2)

def generate_delay_func(f1, f2, l):
    """Given parameters f1, f2, l (relative delays + length between microphones)
    return closure to solve for (r, theta)
    """
    def delay_func(x):
        r, theta = x[0], x[1]
        f = [
            math.sqrt(r*r + l*l - 2*l*r*math.cos(2*math.pi/3 + theta)) -
            math.sqrt(r*r + l*l - 2*l*r*math.cos(theta)) -
            f1,
        ]
        f.append(
            math.sqrt(r*r + l*l - 2*l*r*math.cos(2*math.pi/3 - theta)) -
            math.sqrt(r*r + l*l - 2*l*r*math.cos(theta)) -
            f2
        )
        return f
    return delay_func

def locate(f1, f2, l, r0=5, theta0=(math.pi/6)):
    """Locate position given relative delays f1, f2
    NB: Order of f1, f2 doesn't matter here, but determines which axis
    theta is relative to
    """
    func = generate_delay_func(f1, f2, l)
    r_hat, theta_hat = fsolve(func, [5, math.pi/6])
    return r_hat, theta_hat

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
