from constants.kinect import FREENECT_LED_MODES, FREENECT_LED_MODE_DESCIPTIONS
from service.led.base_led_service import BaseLEDService
from service.tilt.base_tilt_service import BaseTiltService
import freenect


class PhysicalLEDService(BaseLEDService):
  def __init__(self):
    self.pending_led_change = False
  
  def body(self, dev, ctx, led_mode):
    if self.pending_led_change:
      self.pending_led_change = False
    else:
      raise freenect.Kill
    freenect.set_led(dev, led_mode)
    self.pending_led_change = False
    raise freenect.Kill
  
  def set_led_mode(self, led_mode: int) -> None:
    """Set the tilt angle of the Kinect sensor."""
    # The angle should be in the range of -30 to 30 degrees
    if led_mode not in FREENECT_LED_MODES:
      raise Exception(f"invalid led mode: {led_mode}")
    
    print(f'setting led to {FREENECT_LED_MODE_DESCIPTIONS[led_mode]}')
    # freenect.sync_stop()
    self.pending_led_change = True
    body_func = lambda dev, ctx: self.body(dev, ctx, led_mode)
    freenect.runloop(body=body_func, depth=lambda x, y: None)
    # freenect.sync_stop()
    print(f"led mode set to {FREENECT_LED_MODE_DESCIPTIONS[led_mode]}")