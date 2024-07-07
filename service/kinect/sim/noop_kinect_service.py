import numpy as np

from constants.kinect import FREENECT_LED_MODE_DESCIPTIONS, LOOKING_STRAIGHT, LOOKING_UP, LOOKING_DOWN
from service.kinect.base_kinect_service import BaseKinectService


class NoopKinectService(BaseKinectService):
  def __init__(self):
    self._tilt_angle = 0
  
  def get_current_looking_direction(self) -> str:
    if self._tilt_angle > 0:
      looking_direction = LOOKING_UP
    elif self._tilt_angle == 0:
      looking_direction = LOOKING_STRAIGHT
    else:
      looking_direction = LOOKING_DOWN
    print(f'[NOOP] call to get_current_looking_direction, returning {looking_direction}')
    return looking_direction
  
  def set_led_mode(self, led_mode: int) -> None:
    print(f'[NOOP] setting led to {FREENECT_LED_MODE_DESCIPTIONS[led_mode]}')
  
  def do_tilt(self, degrees: int) -> None:
    
    print(f'[NOOP] setting tilt degrees to {degrees}')
  
  def get_video(self) -> np.array:
    print(f'[NOOP] call to get_video')
    return np.zeros(shape=(1, 1))
  
  def get_depth(self) -> np.array:
    print(f'[NOOP] call to get_depth')
    return np.zeros(shape=(1, 1))
    
  
