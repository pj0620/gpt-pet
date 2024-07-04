import numpy as np

from constants.kinect import FREENECT_LED_MODES, FREENECT_LED_MODE_DESCIPTIONS
from service.kinect.base_kinect_service import BaseKinectService
import freenect


NOOP_TILT_DEGREES = -100
NOOP_LED_MODE = -1


class AsyncPhysicalKinectService(BaseKinectService):
  def __init__(self):
    self._update_led = NOOP_LED_MODE
    self._update_deg_tilt = NOOP_TILT_DEGREES
    
    self._last_depth = None
    self._last_rgb = None
    
    context = freenect.init()
    device = freenect.open_device(context, 0)
    freenect.set_depth_mode(device, freenect.RESOLUTION_MEDIUM, freenect.DEPTH_REGISTERED)
    freenect.set_video_mode(device, freenect.RESOLUTION_MEDIUM, freenect.VIDEO_RGB)
    freenect.runloop(body=self._body, depth=self._depth_handler, video=self._rgb_handler, dev=device)
  
  def _body(self, dev, ctx):
    if self._update_deg_tilt != NOOP_TILT_DEGREES:
      freenect.set_tilt_degs(dev, self._update_deg_tilt)
      print(f"tilt degrees set to {self._update_deg_tilt}")
      self._update_deg_tilt = NOOP_TILT_DEGREES
    elif self._update_led != NOOP_LED_MODE:
      freenect.set_led(dev, self._update_led)
      print(f"led mode set to {FREENECT_LED_MODE_DESCIPTIONS[self._update_led]}")
      self._update_led = NOOP_LED_MODE
    
  def _depth_handler(self, dev, data, timestamp):
    print('_depth_handler called ', type(data))
    self._last_depth = data
  
  def _rgb_handler(self, dev, data, timestamp):
    print('_rgb_handler called')
    self._last_rgb = data
  
  def set_led_mode(self, led_mode: int) -> None:
    """Set the tilt angle of the Kinect sensor."""
    # The angle should be in the range of -30 to 30 degrees
    if led_mode not in FREENECT_LED_MODES:
      raise Exception(f"invalid led mode: {led_mode}")
    
    print(f'setting led to {FREENECT_LED_MODE_DESCIPTIONS[led_mode]}')
    self._update_led = led_mode
  
  def do_tilt(self, degrees: int) -> None:
    """Set the tilt angle of the Kinect sensor."""
    # The angle should be in the range of -30 to 30 degrees
    if not (-30 <= degrees <= 30):
      raise Exception(f"invalid tilt degrees={degrees} must be between -30 and 30")
    
    print(f'setting tilt degrees to {degrees}')
    self._update_deg_tilt = degrees
  
  def get_video(self) -> np.array:
    return self._last_rgb
  
  def get_depth(self) -> np.array:
    return self._last_depth
    
  
