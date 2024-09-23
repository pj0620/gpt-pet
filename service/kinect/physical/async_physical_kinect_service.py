import numpy as np
import threading

from constants.kinect import FREENECT_LED_MODES, FREENECT_LED_MODE_DESCIPTIONS, LOOKING_UP, LOOKING_STRAIGHT, \
  LOOKING_DOWN
from service.kinect.base_kinect_service import BaseKinectService
import freenect

NOOP_TILT_DEGREES = -100
NOOP_LED_MODE = -1
DEPTH_FRAME_COUNT = 3


class AsyncPhysicalKinectService(BaseKinectService):
  def __init__(self):
    # set these to signal to thread to update kinect async
    self._update_led = NOOP_LED_MODE
    self._update_deg_tilt = NOOP_TILT_DEGREES
    
    self._last_depth_frames = []
    self._last_rgb = None
    
    # stores current angle
    self._tilt_angle = 0
    
    self.context = freenect.init()
    self.device = freenect.open_device(self.context, 0)
    freenect.set_depth_mode(self.device, freenect.RESOLUTION_MEDIUM, freenect.DEPTH_REGISTERED)
    freenect.set_video_mode(self.device, freenect.RESOLUTION_MEDIUM, freenect.VIDEO_RGB)
    
    # Start the runloop in a new thread
    self.runloop_thread = threading.Thread(target=self._start_runloop)
    self.runloop_thread.daemon = True  # Optional: This makes the thread exit when the main program exits
    self.runloop_thread.start()
  
  def _start_runloop(self):
    freenect.runloop(body=self._body, depth=self._depth_handler, video=self._rgb_handler, dev=self.device)
  
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
    self._last_depth_frames.append(data)
    if len(self._last_depth_frames) > DEPTH_FRAME_COUNT:
      self._last_depth_frames.pop(0)
  
  def _rgb_handler(self, dev, data, timestamp):
    self._last_rgb = data
  
  def set_led_mode(self, led_mode: int) -> None:
    """Set the tilt angle of the Kinect sensor."""
    if led_mode not in FREENECT_LED_MODES:
      raise Exception(f"invalid led mode: {led_mode}")
    
    print(f'setting led to {FREENECT_LED_MODE_DESCIPTIONS[led_mode]}')
    self._update_led = led_mode
  
  def do_tilt(self, degrees: int) -> None:
    """Set the tilt angle of the Kinect sensor."""
    # The angle should be in the range of -30 to 30 degrees
    if not (-30 <= degrees <= 30):
      raise Exception(f"invalid tilt degrees={degrees} must be between -30 and 30")
    
    self._tilt_angle = degrees
    print(f'setting tilt degrees to {degrees}')
    self._update_deg_tilt = degrees
    
  def get_current_looking_direction(self) -> str:
    if self._tilt_angle > 0:
      looking_direction = LOOKING_UP
    elif self._tilt_angle == 0:
      looking_direction = LOOKING_STRAIGHT
    else:
      looking_direction = LOOKING_DOWN
    print(f'[NOOP] call to get_current_looking_direction, returning {looking_direction}')
    return looking_direction
  
  def get_video(self) -> np.array:
    return self._last_rgb
  
  def get_depth(self) -> np.array:
    print('self._last_depth_frames: ', self._last_depth_frames)
    print('res: ', sum(self._last_depth_frames) / DEPTH_FRAME_COUNT)
    return sum(self._last_depth_frames) / DEPTH_FRAME_COUNT
