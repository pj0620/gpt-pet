from typing import Literal

from service.sensor.base_proximity_sensor_adapter import BaseProximitySensorAdapter
from service.sim_adapter import SimAdapter


class Ai2thorProximitySensorAdapter(BaseProximitySensorAdapter):
  def __init__(
    self,
    sim_adapter: SimAdapter
  ):
    self.sim_adapter = sim_adapter
    self.last_event = None
    
  def get_measurements(self) -> dict[Literal['right', 'ahead', 'left', 'back'], str]:
    return self.sim_adapter.proximity_measurements