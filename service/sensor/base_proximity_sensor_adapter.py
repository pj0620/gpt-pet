from abc import ABC
from typing import Literal

from service.sim_adapter import SimAdapter


class BaseProximitySensorAdapter(ABC):
  def get_measurements(self) -> dict[Literal['right', 'ahead', 'left', 'back'], str]:
    """
    :return: measurements from Robot's proximity sensors
    """