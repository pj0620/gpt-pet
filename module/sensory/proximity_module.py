from typing import Any

from PIL import Image

from gptpet_context import GPTPetContext
from module.sensory.base_sensory_module import BaseSensoryModule
from service.sensor.base_proximity_sensor_adapter import BaseProximitySensorAdapter
from service.sim_adapter import SimAdapter


class ProximityModule(BaseSensoryModule):
  def __init__(
      self,
      proximity_adapter: BaseProximitySensorAdapter
  ):
    self.proximity_adapter = proximity_adapter
  
  def build_subconscious_input(self, context: GPTPetContext) -> dict[str, Any]:
    return {'proximity_measurements': self.proximity_adapter.get_measurements()}
