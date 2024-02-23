from abc import ABC

from service.sim_adapter import SimAdapter


class BaseProximitySensorAdapter(ABC):
  def get_measurements(self):
    """
    :return: measurements from Robot's proximity sensors
    """