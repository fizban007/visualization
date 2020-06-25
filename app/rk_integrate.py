import numpy as np
import math

c2 = 0.2
c3 = 0.3
c4 = 0.8
c5 = 8.0/9.0
a21 = 0.2
a31 = 3.0/40.0
a32 = 9.0/40.0
a41 = 44.0/45.0
a42 = -56.0/15.0
a43 = 32.0/9.0
a51 = 19372.0/6561.0
a52 = -25360.0/2187.0
a53 = 64448.0/6561.0
a54 = -212.0/729.0
a61 = 9017.0/3168.0
a62 = -355.0/33.0
a63 = 46732.0/5247.0
a64 = 49.0/176.0
a65 = -5103.0/18656.0
a71 = 35.0/384.0
a73 = 500.0/1113.0
a74 = 125.0/192.0
a75 = -2187.0/6784.0
a76 = 11.0/84.0
e1 = 71.0/57600.0
e3 = -71.0/16695.0
e4 = 71.0/1920.0
e5 = -17253.0/339200.0
e6 = 22.0/525.0
e7 = -1.0/40.0

atol = 1e-6
rtol = 1e-5

beta = 0.04
alpha = 0.2 - beta * 0.75
safe = 0.9
minscale = 0.2
maxscale = 10.0

def RKdy(h, x, y, dydx, f):
    ytemp = y + dydx * h * a21
    k2 = f(x + c2 * h, ytemp)
    ytemp = y + (dydx * a31 + k2 * a32) * h
    k3 = f(x + c3 * h, ytemp)
    ytemp = y + (dydx * a41 + k2 * a42 + k3 * a43) * h
    k4 = f(x + c4 * h, ytemp)
    ytemp = y + (dydx * a51 + k2 * a52 + k3 * a53 + k4 * a54) * h
    k5 = f(x + c5 * h, ytemp)
    ytemp = y + (dydx * a61 + k2 * a62 + k3 * a63 + k4 * a64 + k5 * a65) * h
    k6 = f(x + h, ytemp)
    yout = y + (dydx * a71 + k3 * a73 + k4 * a74 + k5 * a75 + k6 * a76) * h
    dydxout = f(x + h, yout)
    yerr = (dydx * e1 + k3 * e3 + k4 * e4 + k5 * e5 + k6 * e6 + dydxout * e7)
    return yout, dydxout, yerr

def error(y, yout, yerr):
    sk = atol + np.maximum(y, yout) * rtol
    tmp = yerr / sk
    err = np.sqrt(np.sum(tmp*tmp))
    if hasattr(tmp, "__len__"):
        return err / len(tmp)
    else:
        return err

def find_hnext(err, h, prev_reject, prev_err):
    scale = 1.0
    if err <= 1.0:
        if err == 0.0:
            scale = maxscale
        else:
            scale = safe * math.pow(err, -alpha) * math.pow(prev_err, beta)
            if scale < minscale: scale = minscale
            if scale > maxscale: scale = maxscale
        hnext = h
        if prev_reject:
            hnext = h * min(scale, 1.0)
        else:
            hnext = h * scale
        return True, hnext, max(err, 1.0e-4)
    else:
        scale = max(safe * math.pow(err, -alpha), minscale)
        hnext = h * scale
        return False, hnext, err
    
def RKstep(h, x, y, dydx, f, prev_rej, prev_err):
    hnext = h
    while True:
        yout, dydxout, yerr = RKdy(h, x, y, dydx, f)
        err = error(y, yout, yerr)
        success, hnext, prev_err = find_hnext(err, h, prev_rej, prev_err)
        prev_rej = not success
        if success: break
        else:
            h = hnext
    return x + h, yout, dydxout, hnext, prev_rej, prev_err

def RK_integrate(x0, y0, h0, f, end_cond):
    xs = [x0]
    ys = [y0]
    h = h0
    dydx = f(x0, y0)
    prev_rej = False
    prev_err = 1.0e-4
    x = x0
    y = y0
    num = 0
    while not end_cond(x, y) and num < 10000:
        x, y, dydx, h, prev_rej, prev_err = RKstep(h, x, y, dydx, f, prev_rej, prev_err)
        xs.append(np.copy(x))
        ys.append(np.copy(y))
        num += 1
    return np.array(xs), np.array(ys)

def Euler_integrate(x0, y0, h, f, end_cond, n_max=10000):
    xs = [x0]
    ys = [y0]
    x = np.copy(x0)
    y = np.copy(y0)
    num = 0
    while not end_cond(x, y) and num < n_max:
        y += f(x, y) * h
        x += h
        xs.append(np.copy(x))
        ys.append(np.copy(y))
        num += 1
    return np.array(xs), np.array(ys)
