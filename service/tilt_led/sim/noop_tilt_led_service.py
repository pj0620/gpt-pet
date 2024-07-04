from constants.kinect import FREENECT_LED_MODE_DESCIPTIONS
from service.tilt_led.base_tilt_led_service import BaseLEDService, BaseTiltLedService
from service.tilt.base_tilt_service import BaseTiltService


class NoopTiltLedService(BaseTiltLedService):
  
  def set_led_mode(self, led_mode: int) -> None:
    print(f'[NOOP] setting led to {FREENECT_LED_MODE_DESCIPTIONS[led_mode]}')
  
  def do_tilt(self, degrees: int) -> None:
    print(f'[NOOP] setting tilt degrees to {degrees}')
