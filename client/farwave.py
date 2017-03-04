from math import atan2, radians, degrees, sin, cos, acos, sqrt
import numpy as np
import locate

from enum import Enum
class MIC_PAIRS(Enum):
    MIC0_1 = 1
    MIC2_0 = 2
    MIC1_2 = 3

def wrap_angle(angle):
    return (angle + np.pi) % (2 * np.pi ) - np.pi

def combine_angles(angles, errors):
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

    normalized_delay = float(delay)/abs(max_delay)
    ang_raw = acos(normalized_delay)
    error_est = 1/sqrt(1-normalized_delay**2) # derivative of arccos, measures sensitivity of far wave
    if not pos_ang:
        ang_raw = -ang_raw

    if pair_num == MIC_PAIRS.MIC0_1:
        ang = wrap_angle(ang_raw + np.pi/6)

    elif pair_num == MIC_PAIRS.MIC2_0:
        ang = wrap_angle(ang_raw + 5*np.pi/6)

    else: # pair_num == MIC_PAIRS.MIC1_2:
        ang = wrap_angle(ang_raw - np.pi/2)

    return (ang, error_est)

def calc_angle(delays, l):
    angles = []
    errors = []
    max_delay = locate.calc_max_delay(l)

    for mic_pair in MIC_PAIRS:
        far_ang = calc_far_wave_angle(delays, max_delay, mic_pair)
        angles.append(far_ang[0])
        errors.append(far_ang[1])

    print("Angles: %r\nErrors: %r\n" % ([degrees(ang) for ang in angles], errors))

    final_ang = degrees(combine_angles(angles, errors))
    return final_ang