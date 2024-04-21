from abc import ABC
from typing import Literal

from service.sim_adapter import SimAdapter


class BaseDeviceIOAdapter(ABC):
  def get_measurements(self) -> dict[Literal['right', 'ahead', 'left', 'back'], str]:
    """
    :return: measurements from Robot's proximity sensors
    """
  
  def set_color(
      self,
      color: str
  ) -> None:
    """ sets color of onboard leds
    """
    pass