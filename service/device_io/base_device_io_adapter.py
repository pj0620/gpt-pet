from abc import ABC, abstractmethod
from typing import Literal


class BaseDeviceIOAdapter(ABC):
  @abstractmethod
  def get_measurements(self) -> dict[Literal['right', 'ahead', 'left', 'back'], str]:
    """
    :return: measurements from Robot's proximity sensors
    """
    pass
  
  # opting to use kinect leds for now
  @abstractmethod
  def set_color(
      self,
      color: str
  ) -> None:
    """ sets color of onboard leds
    """
    pass