from math import sin, cos, pi

import numpy
import numpy as np


def get_rotation_vector(x, y, z):
  t = y * 2 * pi / 360
  
  return np.array([sin(t), 0, cos(t)])

def dict_to_array(d_vect: dict[str, float]) -> numpy.array:
  return numpy.array([
    d_vect['x'],
    d_vect['y'],
    d_vect['z'],
  ])

def array_to_dict(arr: numpy.array) -> dict[str, float]:
  return dict(
    x=arr[0],
    y=arr[1],
    z=arr[2]
  )