from service.led.base_led_service import BaseLEDService
from service.tilt.base_tilt_service import BaseTiltService


class NoopLEDService(BaseLEDService):
  def do_tilt(self, degrees: int) -> None:
    print(f'setting tilt to {degrees}')
