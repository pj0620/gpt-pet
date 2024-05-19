from typing import Any

from gptpet_context import GPTPetContext
from module.sensory.base_sensory_module import BaseSensoryModule
from service.device_io.base_device_io_adapter import BaseDeviceIOAdapter


class ProximityModule(BaseSensoryModule):
  def __init__(
      self,
      device_io_adapter: BaseDeviceIOAdapter
  ):
    self.device_io_adapter = device_io_adapter
    self.name = "proximity module"
  
  def build_subconscious_input(self, context: GPTPetContext) -> dict[str, Any]:
    return {'proximity_measurements': self.device_io_adapter.get_measurements()}
