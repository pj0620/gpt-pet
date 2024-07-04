from constants.kinect import FREENECT_LED_MODES, FREENECT_LED_MODE_DESCIPTIONS
from service.tilt_led.base_tilt_led_service import BaseTiltLedService
import freenect


NOOP_TILT_DEGREES = -100
NOOP_LED_MODE = -1


class SyncPhysicalTiltLedService(BaseTiltLedService):
  
  def set_led_mode(self, led_mode: int) -> None:
    """Set the tilt angle of the Kinect sensor."""
    # The angle should be in the range of -30 to 30 degrees
    if led_mode not in FREENECT_LED_MODES:
      raise Exception(f"invalid led mode: {led_mode}")
    
    print(f'setting led to {FREENECT_LED_MODE_DESCIPTIONS[led_mode]}')
    freenect.freenect_set_tilt_degs()
  
  def do_tilt(self, degrees: int) -> None:
    """Set the tilt angle of the Kinect sensor."""
    # The angle should be in the range of -30 to 30 degrees
    if not (-30 <= degrees <= 30):
      raise Exception(f"invalid tilt degrees={degrees} must be between -30 and 30")
    
    print(f'setting tilt degrees to {degrees}')
    self._update_deg_tilt = degrees
    freenect.sync_stop()
    freenect.runloop(body=self._body, depth=lambda x, y: None)
    freenect.sync_stop()
