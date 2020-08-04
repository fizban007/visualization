import numpy as np
import math
import hashlib
import json
import base64
import os.path as path
from pathlib import Path
import os
import glob
import threading
from app.rk_integrate import Euler_integrate, RK4_integrate
from app.datalib import Data


class Bf:
    def __init__(self, data):
        self.Bx = data.Bx
        self.By = data.By
        self.Bz = data.Bz
        self.x0 = data._conf["lower"][0]
        self.y0 = data._conf["lower"][1]
        self.z0 = data._conf["lower"][2]
        self.dx = data._conf["size"][0] / data._conf["N"][0] * data._conf["downsample"]
        self.dy = data._conf["size"][1] / data._conf["N"][1] * data._conf["downsample"]
        self.dz = data._conf["size"][2] / data._conf["N"][2] * data._conf["downsample"]

    def interp(self, f, x, y, z):
        nx = int(math.floor((x - self.x0) / self.dx))
        ny = int(math.floor((y - self.y0) / self.dy))
        nz = int(math.floor((z - self.z0) / self.dz))
        delx = x - self.x0 - nx * self.dx
        dely = y - self.y0 - ny * self.dy
        delz = z - self.z0 - nz * self.dz
        #     print(delx, dely, delz)
        f00 = (1.0 - delz) * f[nz, ny, nx] + delz * f[nz + 1, ny, nx]
        f01 = (1.0 - delz) * f[nz, ny, nx + 1] + delz * f[nz + 1, ny, nx + 1]
        f10 = (1.0 - delz) * f[nz, ny + 1, nx] + delz * f[nz + 1, ny + 1, nx]
        f11 = (1.0 - delz) * f[nz, ny + 1, nx + 1] + delz * f[nz + 1, ny + 1, nx + 1]
        f0 = (1.0 - dely) * f00 + dely * f10
        f1 = (1.0 - dely) * f01 + dely * f11
        return (1.0 - delx) * f0 + delx * f1

    def value(self, x, y):
        B = np.array(
            [
                self.interp(self.Bx, y[0], y[1], y[2]),
                self.interp(self.By, y[0], y[1], y[2]),
                self.interp(self.Bz, y[0], y[1], y[2]),
            ]
        )
        return B / np.sqrt(sum(B * B))

    def value_neg(self, x, y):
        return -self.value(x, y)


def seed_plane_x(x, n_seeds, y_lims=(-1, 1), z_lims=(-1, 1)):
    seeds = []
    for n in range(n_seeds):
        y = y_lims[0] + (y_lims[0] - y_lims[1]) * np.random.random_sample()
        z = z_lims[0] + (z_lims[0] - z_lims[1]) * np.random.random_sample()
        seeds.append(np.array([x, y, z]))
    return seeds


def seed_plane_y(y, n_seeds, z_lims=(-1, 1), x_lims=(-1, 1)):
    seeds = []
    for n in range(n_seeds):
        x = x_lims[0] + (x_lims[0] - x_lims[1]) * np.random.random_sample()
        z = z_lims[0] + (z_lims[0] - z_lims[1]) * np.random.random_sample()
        seeds.append(np.array([x, y, z]))
    return seeds


def seed_plane_z(z, n_seeds, x_lims=(-1, 1), y_lims=(-1, 1)):
    seeds = []
    for n in range(n_seeds):
        y = y_lims[0] + (y_lims[0] - y_lims[1]) * np.random.random_sample()
        x = x_lims[0] + (x_lims[0] - x_lims[1]) * np.random.random_sample()
        seeds.append(np.array([x, y, z]))
    return seeds


def seed_spherical(r, thetas, phis):
    seeds = []
    for th in thetas:
        for ph in phis:
            seeds.append(
                r
                * np.array(
                    [np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), np.cos(th)]
                )
            )
    return seeds


def seed_spherical_random(r, n_seeds):
    seeds = []
    for n in range(n_seeds):
        mu = np.random.random_sample() * 2.0 - 1.0
        th = np.arccos(mu)
        ph = 2 * np.pi * np.random.random_sample()
        p = r * np.array([np.sin(th) * np.sin(ph), np.sin(th) * np.cos(ph), np.cos(th)])
        seeds.append(p)
    return seeds


def gen_seed_points(seed_config):
    seeds = []
    if isinstance(seed_config, list):
        for c in seed_config:
            seeds.extend(gen_seed_points(c))
    else:
        if seed_config["name"] == "spherical_random":
            seeds.extend(
                seed_spherical_random(seed_config["r"], seed_config["n_seeds"])
            )
        elif seed_config["name"] == "spherical":
            seeds.extend(
                seed_spherical(
                    seed_config["r"], seed_config["thetas"], seed_config["phis"]
                )
            )
        elif seed_config["name"] == "plane_x":
            seeds.extend(
                seed_plane_x(
                    seed_config["x"],
                    seed_config["n_seeds"],
                    seed_config["y_lims"],
                    seed_config["z_lims"],
                )
            )
        elif seed_config["name"] == "plane_y":
            seeds.extend(
                seed_plane_x(
                    seed_config["y"],
                    seed_config["n_seeds"],
                    seed_config["z_lims"],
                    seed_config["x_lims"],
                )
            )
        elif seed_config["name"] == "plane_z":
            seeds.extend(
                seed_plane_x(
                    seed_config["z"],
                    seed_config["n_seeds"],
                    seed_config["x_lims"],
                    seed_config["y_lims"],
                )
            )
    return seeds


def hash_config(seed_config):
    dig = hashlib.sha1(json.dumps(seed_config, sort_keys=True).encode("UTF-8")).digest()
    return base64.urlsafe_b64encode(dig[:6]).decode("ascii")


def integrate_fields_with_seeds(p_seeds, data):
    data_b = Bf(data)

    box_size = abs(max(data._conf["lower"]))

    def end_box(x, y):
        r = np.sqrt(sum(y * y))
        dist = np.max(abs(y))
        return r < 1.0 or dist > 0.9 * box_size

    lines = []
    for p in p_seeds:
        xs, ys = RK4_integrate(0.0, p, 0.1, data_b.value, end_box, 3000)
        xs2, ys2 = RK4_integrate(0.0, p, 0.1, data_b.value_neg, end_box, 3000)
        if len(ys) > 100:
            lines.append(np.concatenate((ys[:0:-1], ys2))[::5])
        elif len(ys) > 30:
            lines.append(np.concatenate((ys[:0:-1], ys2))[::2])
        else:
            lines.append(np.concatenate((ys[:0:-1], ys2)))
    return lines


def integrate_fields(seeds, config_hash, data, step):
    data.load_fld(step)
    lines = np.array(integrate_fields_with_seeds(seeds, data), dtype=object)
    return lines


def get_fieldline(seed_config, data_path, step):
    h = hash_config(seed_config)
    cache_path = path.join(data_path, "fieldlines")
    cache_file = path.join(cache_path, f"{step:05d}.{h}.npy")
    if path.exists(cache_file):
        lines = np.load(cache_file, allow_pickle=True)
        return lines
    else:
        return []

def remove_cache(data_path, seed_config=None):
    cache_path = Path(data_path) / "fieldlines"
    if seed_config is None:
        for f in cache_path.glob("*.npy"):
            f.unlink()
    else:
        pass

class IntegrationThread(threading.Thread):
    def __init__(self, seed_config, data_path):
        self.progress = 0.0
        self.config = seed_config
        self.data = Data(data_path)
        super().__init__()

    def run(self):
        cache_path = path.join(self.data._path, "fieldlines")
        if not path.exists(cache_path):
            os.mkdir(cache_path)

        conf_hash = hash_config(self.config)
        seeds = gen_seed_points(self.config)

        for step in self.data.fld_steps:
            cache_file = path.join(cache_path, f"{step:05d}.{conf_hash}.npy")
            if not path.exists(cache_file):
                lines = integrate_fields(seeds, conf_hash, self.data, step)
                np.save(cache_file, lines)
            self.progress += 100.0 / len(self.data.fld_steps)
            print(f"fieldlines {step}/{len(self.data.fld_steps)}")
