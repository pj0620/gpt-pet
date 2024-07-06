from abc import ABC

import numpy as np


class BaseKinectService(ABC):
  def set_led_mode(self, led_mode: int) -> None:
    """
    sets led based on kinect led modes
    TODO: create more general way to do this
    :param led_mode: led mode from kinect
    :return: None
    """
    pass
  
  def do_tilt(self, degrees: int) -> None:
    """
    Tilts GPTPet
    :param degrees: degrees to tile
    :return: None
    """
    pass
  
  def get_video(self) -> np.array:
    """
    gets last rgb image from kinect
    :return: rgb image
    """
    pass
  
  def get_depth(self) -> np.array:
    """
    gets last depth image from kinect
    :return: depth image
    """
    pass
