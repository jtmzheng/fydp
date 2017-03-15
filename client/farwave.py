from math import atan2, radians, degrees, sin, cos, acos, sqrt
import numpy as np
import locate

from enum import Enum

SENSITIVITY_THRESH = 0.20

class MIC_PAIRS(Enum):
    MIC0_1 = 0
    MIC2_0 = 1
    MIC1_2 = 2

MIC_PAIRS_TO_ENUM = {
    (0, 1): MIC_PAIRS.MIC0_1,
    (0, 2): MIC_PAIRS.MIC2_0,
    (1, 2): MIC_PAIRS.MIC1_2
}

def wrap_angle(angle):
    """ Wrap angle in [-pi, pi] radians
    """
    return (angle + np.pi) % (2. * np.pi) - np.pi

def combine_angles(angles, errors):
    """ FIXME
    """
    a0 = wrap_angle(angles[0])
    a1 = wrap_angle(angles[1])
    a2 = wrap_angle(angles[2])

    e0_2 = errors[0]**2
    e1_2 = errors[1]**2
    e2_2 = errors[2]**2

    denum = float(2*(e0_2+e1_2+e2_2))
    w0 = (e1_2 + e2_2)/denum
    w1 = (e0_2 + e2_2)/denum
    w2 = (e0_2 + e1_2)/denum

    return atan2(w0 * sin(a0) + w1 * sin(a1) + w2 * sin(a2),
                 w0 * cos(a0) + w1 * cos(a1) + w2 * cos(a2))

def calc_far_wave_angle(delays, max_delay, pair_num):
    """ FIXME
    """
    pos_ang = True
    if pair_num == MIC_PAIRS.MIC0_1:
        delay = delays[0][1]
        pos_ang = np.mean((delays[2][1], delays[2][0])) > 0
    elif pair_num == MIC_PAIRS.MIC2_0:
        delay = delays[2][0]
        pos_ang = np.mean((delays[1][0], delays[1][2])) > 0
    else: # pair_num == MIC_PAIRS.MIC1_2:
        delay = delays[1][2]
        pos_ang = np.mean((delays[0][1], delays[0][2])) > 0

    normalized_delay = float(delay) / abs(max_delay)
    ang_raw = acos(normalized_delay)

    # Derivative of acos used to quantify sensitivity of far wave
    error_est = 1. / sqrt(1. - normalized_delay**2)
    if not pos_ang:
        ang_raw = -ang_raw

    if pair_num == MIC_PAIRS.MIC0_1:
        ang = wrap_angle(ang_raw + np.pi/6)
    elif pair_num == MIC_PAIRS.MIC2_0:
        ang = wrap_angle(ang_raw + 5*np.pi/6)
    else: # pair_num == MIC_PAIRS.MIC1_2:
        ang = wrap_angle(ang_raw - np.pi/2)

    return (ang, error_est)

def map_ccw(ang):
    """ Map the angle from CW to CCW and from [-180, 180] to [0, 360]
    """
    ang = -ang                                  # CW -> CCW
    if ang < 0:
        ang = 360. - np.abs(ang)    # [-180, 180] -> [0, 360]
    return ang

def calc_angle(delays, l, near_pair=None):
    """ FIXME
    """
    angles = []
    errors = []
    max_delay = locate.calc_max_delay(l)

    for mic_pair in MIC_PAIRS:
        far_ang = calc_far_wave_angle(delays, max_delay, mic_pair)
        angles.append(far_ang[0])
        errors.append(far_ang[1])

    print 'Angles: %r\nErrors: %r\n' % ([map_ccw(degrees(ang)) for ang in angles], errors)

    # Map final angle to CCW and [0, 360]
    final_ang = map_ccw(degrees(combine_angles(angles, errors)))

    if near_pair is None:
        print 'Angle (CCW): %f' % final_ang
        return final_ang

    min_err = np.min(np.abs(errors))
    for i in range(len(errors)):
        for j in range(i + 1, len(errors)):
            print 'DEL_ERR: %f' % np.abs(errors[i] - errors[j])
            print 'Error: %f, %f, %r' % (np.abs(errors[i] - errors[j]), min_err, str(np.isclose(min_err, min(errors[i], errors[j]))))
            if (np.abs(errors[i] - errors[j]) < SENSITIVITY_THRESH and
                np.isclose(min(errors[i], errors[j]), min_err)):
                final_ang = map_ccw(degrees(angles[MIC_PAIRS_TO_ENUM[near_pair].value]))
                print 'Setting final_ang to %f' % final_ang
                break

    print 'Angle (CCW): %f' % final_ang
    return final_ang

