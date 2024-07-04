import numpy as np

from constants.kinect import FREENECT_LED_MODE_DESCIPTIONS
from service.kinect.base_kinect_service import BaseKinectService


class NoopKinectService(BaseKinectService):
  
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
    
  
