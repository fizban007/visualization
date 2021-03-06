import numpy as np
import scipy.interpolate as interp

def resample(data, shape):
    """
    Resample the 3d data into a given shape. The axis order is assumed to
    be the same as TRISTAN-MP
    """
    z = np.linspace(0,1,data.shape[0])
    y = np.linspace(0,1,data.shape[1])
    x = np.linspace(0,1,data.shape[2])
    new_z = np.linspace(0,1,shape[0])
    new_y = np.linspace(0,1,shape[1])
    new_x = np.linspace(0,1,shape[2])

    interpx = interp.interp1d(x, data, kind='linear')
    tmp1 = interpx(new_x)

    interpy = interp.interp1d(y, tmp1, axis=1, kind='linear')
    tmp2 = interpy(new_y)

    interpz = interp.interp1d(z, tmp2, axis=0, kind='linear')
    return interpz(new_z)

def just_above_power(n):
    for i in range(4, 11):
        target = 1 << i
        if target <= n and target > n*0.8:
            return True, target
    return False, 0

def just_below_power(n):
    for i in range(4, 11):
        target = 1 << i
        if target >= n and target < n*1.2:
            return True, target
    return False, 0

def closest_power(n):
    target = 1
    for i in range(4, 11):
        p = 1 << i
        if p > n: return target
        else: target = p
    return target

def round_to_even(n):
    return (n // 2) * 2

def is_odd(num):
    return num & 0x1

def is_power_of_two(n):
    return (n & (n-1) == 0) and n != 0

def adaptive_resample(data):
    """Adaptively resample the 3d data. If the original dimension is close
    to a power of 2, then it is simply padded or cut (from the sides) to
    the target power of 2. If not, then it is simply interpolated onto a
    smaller grid of size power of 2."""
    # z direction
    b, t = just_above_power(data.shape[0])
    if b:
        print("%d dir 0 is just above %d" % (data.shape[0], t))
        offset = (data.shape[0] - t) // 2
        tmp1 = data[offset:round_to_even(data.shape[0])-offset,:,:]
    else:
        b, t = just_below_power(data.shape[0])
        if b:
            print("dir 0 is just below %d" % t)
            pad = (t - data.shape[0]) // 2
            tmp1 = np.pad(data, ((pad, pad + is_odd(data.shape[0])),(0,0),(0,0)),
                          'constant', constant_values=0)
        else:
            print("dir 0 requires interpolation")
            z = np.linspace(0,1,data.shape[0])
            new_z = np.linspace(0,1,closest_power(data.shape[0]))
            interpz = interp.interp1d(z, data, axis=0, kind='linear')
            tmp1 = interpz(new_z)

    # y direction
    b, t = just_above_power(data.shape[1])
    if b:
        print("dir 1 is just above %d" % t)
        offset = (data.shape[1] - t) // 2
        tmp2 = tmp1[:,offset:round_to_even(data.shape[1])-offset,:]
    else:
        b, t = just_below_power(data.shape[1])
        if b:
            print("dir 1 is just below %d" % t)
            pad = (t - data.shape[1]) // 2
            tmp2 = np.pad(tmp1, ((0,0),(pad, pad + is_odd(data.shape[1])),(0,0)),
                          'constant', constant_values=0)
        else:
            print("dir 1 requires interpolation")
            y = np.linspace(0,1,data.shape[1])
            new_y = np.linspace(0,1,closest_power(data.shape[1]))
            interpy = interp.interp1d(y, tmp1, axis=1, kind='linear')
            tmp2 = interpy(new_y)

    # x direction
    b, t = just_above_power(data.shape[2])
    if b:
        print("dir 2 is just above %d" % t)
        offset = (data.shape[2] - t) // 2
        result = tmp2[:,:,offset:round_to_even(data.shape[2])-offset]
    else:
        b, t = just_below_power(data.shape[2])
        if b:
            print("dir 2 is just below %d" % t)
            pad = (t - data.shape[2]) // 2
            result = np.pad(tmp2, ((0,0),(0,0),(pad, pad + is_odd(data.shape[2]))),
                            'constant', constant_values=0)
        else:
            print("dir 2 requires interpolation")
            x = np.linspace(0,1,data.shape[2])
            new_x = np.linspace(0,1,closest_power(data.shape[2]))
            interpx = interp.interp1d(x, tmp2, axis=2, kind='linear')
            result = interpx(new_x)

    return result
