from abc import ABC, abstractmethod

import numpy as np


class BaseKinectService(ABC):
  @abstractmethod
  def get_current_looking_direction(self) -> str:
    """
    returns where gptpet is currently looking
    :return: up/down/straight
    """
  
  @abstractmethod
  def set_led_mode(self, led_mode: int) -> None:
    """
    sets led based on kinect led modes
    TODO: create more general way to do this
    :param led_mode: led mode from kinect
    :return: None
    """
    pass
  
  @abstractmethod
  def do_tilt(self, degrees: int) -> None:
    """
    Tilts GPTPet
    :param degrees: degrees to tile
    :return: None
    """
    pass
  
  @abstractmethod
  def get_video(self) -> np.array:
    """
    gets last rgb image from kinect
    :return: rgb image
    """
    pass
  
  @abstractmethod
  def get_depth(self) -> np.array:
    """
    gets last depth image from kinect
    :return: depth image
    """
    pass
