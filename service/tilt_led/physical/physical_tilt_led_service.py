from constants.kinect import FREENECT_LED_MODES, FREENECT_LED_MODE_DESCIPTIONS
from service.tilt_led.base_tilt_led_service import BaseTiltLedService
import freenect


NOOP_TILT_DEGREES = -100
NOOP_LED_MODE = -1


class PhysicalTiltLedService(BaseTiltLedService):
  def __init__(self):
    self.update_led = NOOP_LED_MODE
    self.update_deg_tilt = NOOP_TILT_DEGREES
  
  def body(self, dev, ctx):
    if self.update_deg_tilt != NOOP_TILT_DEGREES:
      freenect.set_tilt_degs(dev, self.update_deg_tilt)
      print(f"tilt degrees set to {self.update_deg_tilt}")
      self.update_deg_tilt = NOOP_TILT_DEGREES
    if self.update_led != NOOP_LED_MODE:
      freenect.set_led(dev, self.update_led)
      print(f"led mode set to {FREENECT_LED_MODE_DESCIPTIONS[self.update_led]}")
      self.update_led = NOOP_LED_MODE
  
  def set_led_mode(self, led_mode: int) -> None:
    """Set the tilt angle of the Kinect sensor."""
    # The angle should be in the range of -30 to 30 degrees
    if led_mode not in FREENECT_LED_MODES:
      raise Exception(f"invalid led mode: {led_mode}")
    
    print(f'setting led to {FREENECT_LED_MODE_DESCIPTIONS[led_mode]}')
    self.update_led = led_mode
    freenect.runloop(body=self.body, depth=lambda x, y: None)
  
  def do_tilt(self, degrees: int) -> None:
    """Set the tilt angle of the Kinect sensor."""
    # The angle should be in the range of -30 to 30 degrees
    if -30 <= degrees <= 30:
      raise Exception(f"invalid tilt degrees={degrees} must be between -30 and 30")
    
    print(f'setting tilt degrees to {degrees}')
    self.update_deg_tilt = degrees
    freenect.runloop(body=self.body, depth=lambda x, y: None)
