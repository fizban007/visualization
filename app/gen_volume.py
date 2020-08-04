from PIL import Image
import math
import numpy as np
import io
import threading
import os
import os.path as path
from app.datalib import Data
from app.interp import resample, is_power_of_two

def halve_image(image):
    rows, cols, planes = image.shape
    image = image.astype('uint16')
    image = image.reshape(rows // 2, 2, cols // 2, 2, planes)
    image = image.sum(axis=3).sum(axis=1)
    return ((image + 2) >> 2).astype('uint8')

def mipmap(image):
    img = image.copy()
    rows, cols, planes = image.shape
    mipmap = np.zeros((rows, cols * 3 // 2, planes), dtype='uint8')
    mipmap[:, :cols, :] = img
    row = 0
    while rows > 1:
        img = halve_image(img)
        rows = img.shape[0]
        mipmap[row:row + rows, cols:cols + img.shape[1], :] = img
        row += rows
    return mipmap

def resample_array(array, res):
    # FIXME: Here we assumed the array is 3D. Potential technical debt
    if array.shape[0] != res:
        return resample(array, (res, res, res))
    else:
        return array

def tile_size(res):
    if res >= 1024:
        tile_x = 32
    elif res >= 256:
        tile_x = 16
    elif res >= 64:
        tile_x = 8
    elif res >= 16:
        tile_x = 4
    elif res >= 4:
        tile_x = 2
    else:
        tile_x = 1
    return tile_x, res // tile_x

# def gen_tiled_png(array, max_val, res=512):
#     # Always change res to the closest power of 2
#     if not interp.is_power_of_two(res):
#         res = pow(2, int(math.log2(res) + 0.5))
#     data = resample_array(array, res)

#     tile_x, tile_y = tile_size(res)
#     img_width = tile_x * data.shape[2]
#     img_height = tile_y * data.shape[1]

#     red = np.minimum(data*256./max_val, 255).astype('uint8')
#     img = red.reshape(tile_y, tile_x, data.shape[2], data.shape[1]).swapaxes(1, 2).reshape(img_width, img_height)
#     img_io = io.BytesIO()
#     # Image.frombytes()

def gen_tiled_png(arrays, max_vals, res=512):
    # Always change res to the closest power of 2
    if not is_power_of_two(res):
        res = pow(2, int(math.log2(res) + 0.5))

    tile_x, tile_y = tile_size(res)
    if not isinstance(arrays, list) and not isinstance(arrays, tuple):
        raise TypeError("Input arrays should be a list or a tuple!")
    if not isinstance(max_vals, list) and not isinstance(max_vals, tuple):
        raise TypeError("Input max_vals should be a list or a tuple!")
    if len(arrays) != len(max_vals):
        raise RuntimeError("The two input arrays should have matching lengths!")
    else:
        img_width = tile_x * arrays[0].shape[2];
        img_height = tile_y * arrays[0].shape[1];
        img = np.zeros((img_width, img_height))
        for i in range(len(arrays)):
            img += (np.minimum(arrays[i]*256./max_vals[i], 255).astype('uint32') << (8 * i)).reshape(
                tile_y, tile_x, arrays[0].shape[2], arrays[0].shape[1]).swapaxes(1, 2).reshape(img_width, img_height)
        img = Image.frombytes('RGBA', img.shape, img)
        # img = mipmap(img)
        # img_io = io.BytesIO()
        # img.save(img_io, format='png', compress_level=1)
        return img

class VolumeThread(threading.Thread):
    def __init__(self, data_path, res):
        self.progress = 0.0
        self.data = Data(data_path)
        self.res = res
        super().__init__()

    def run(self):
        cache_path = path.join(self.data._path, "volume_data")
        if not path.exists(cache_path):
            os.mkdir(cache_path)

        for step in self.data.fld_steps:
            self.data.load(step)
            img = gen_tiled_png((self.data.J), (np.max(self.data.J)), self.res)
            img.save(path.join(cache_path, f"{step:05d}.{self.res}.png"))
            self.progress += 100.0 / len(self.data.fld_steps)
            print(f"volume {step}/{len(self.data.fld_steps)}")
