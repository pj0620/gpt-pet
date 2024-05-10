from typing import Literal

from service.device_io.base_device_io_adapter import BaseDeviceIOAdapter
from service.sim_adapter import SimAdapter


class Ai2thorDeviceIOAdapter(BaseDeviceIOAdapter):
  def __init__(
    self,
    sim_adapter: SimAdapter
  ):
    self.sim_adapter = sim_adapter
    self.last_event = None
    
  def get_measurements(self) -> dict[Literal['right', 'ahead', 'left', 'back'], str]:
    return self.sim_adapter.proximity_measurements
  
  def set_color(
      self,
      color: str
  ) -> None:
    print('setting color to ', color)