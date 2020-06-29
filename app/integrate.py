from app.rk_integrate import Euler_integrate, RK_integrate
import numpy as np
import math

class Bf:
    def __init__(self, data):
        B = np.sqrt(data.Bx * data.Bx + data.By * data.By + data.Bz * data.Bz)
        self.Bx = data.Bx / B
        self.By = data.By / B
        self.Bz = data.Bz / B
        self.x0 = data._conf['lower'][0]
        self.y0 = data._conf['lower'][1]
        self.z0 = data._conf['lower'][2]
        self.dx = data._conf['size'][0] / data._conf['N'][0] * data._conf['downsample']
        self.dy = data._conf['size'][1] / data._conf['N'][1] * data._conf['downsample']
        self.dz = data._conf['size'][2] / data._conf['N'][2] * data._conf['downsample']

    def interp(self, f, x, y, z):
        nx = int(math.floor((x - self.x0) / self.dx))
        ny = int(math.floor((y - self.y0) / self.dy))
        nz = int(math.floor((z - self.z0) / self.dz))
        delx = x - self.x0 - nx * self.dx
        dely = y - self.y0 - ny * self.dy
        delz = z - self.z0 - nz * self.dz
    #     print(delx, dely, delz)
        f00 = (1.0 - delz) * f[nz,ny,nx] + delz * f[nz+1,ny,nx]
        f01 = (1.0 - delz) * f[nz,ny,nx+1] + delz * f[nz+1,ny,nx+1]
        f10 = (1.0 - delz) * f[nz,ny+1,nx] + delz * f[nz+1,ny+1,nx]
        f11 = (1.0 - delz) * f[nz,ny+1,nx+1] + delz * f[nz+1,ny+1,nx+1]
        f0 = (1.0 - dely) * f00 + dely * f10
        f1 = (1.0 - dely) * f01 + dely * f11
        return (1.0 - delx) * f0 + delx * f1

    def value(self, x, y):
        B = np.array([self.interp(self.Bx, y[0], y[1], y[2]),
                      self.interp(self.By, y[0], y[1], y[2]),
                      self.interp(self.Bz, y[0], y[1], y[2])])
        return B

    def value_neg(self, x, y):
        return -self.value(x, y)


def gen_seed_points(r_seed, n_samples, p_seeds):
    for n in range(n_samples):
        mu = np.random.random_sample() * 2.0 - 1.0
        th = np.arccos(mu)
        ph = 2*np.pi*np.random.random_sample()
        p = r_seed * np.array([np.sin(th) * np.sin(ph),
                               np.sin(th) * np.cos(ph),
                               np.cos(th)])
        p_seeds.append(p)

def integrate_fields(p_seeds, data):
    data_b = Bf(data)

    box_size = abs(max(data._conf['lower']))

    def end_box(x, y):
        r = np.sqrt(sum(y*y))
        dist = np.max(abs(y))
        return r < 1.0 or dist > 0.9 * box_size

    lines = []
    for p in p_seeds:
        xs, ys = Euler_integrate(0.0, p, 0.05, data_b.value, end_box, 3000)
        #xs, ys = RK_integrate(0.0, p, 0.5, data_b.value, end_box, 3000)
        xs2, ys2 = Euler_integrate(0.0, p, 0.05, data_b.value_neg, end_box, 3000)
        #xs2, ys2 = RK_integrate(0.0, p, 0.5, data_b.value, end_box, 3000)
        if len(ys) > 100:
            lines.append(np.concatenate((ys[:0:-1], ys2))[::10])
        elif len(ys) > 30:
            lines.append(np.concatenate((ys[:0:-1], ys2))[::5])
        else:
            lines.append(np.concatenate((ys[:0:-1], ys2)))
    return lines
