from math import sin, cos, pi

import numpy as np


def get_rotation_vector(x, y, z):
  t = y * 2 * pi / 360
  
  return np.array([sin(t), 0, cos(t)])