from typing import Any

from gptpet_context import GPTPetContext
from module.sensory.base_sensory_module import BaseSensoryModule
from service.sim_adapter.base_sim_adapter import BaseSimAdapter


class Ai2ThorCameraModule(BaseSensoryModule):
  def __init__(
      self,
      sim_adapter: BaseSimAdapter
  ):
    self.sim_adapter = sim_adapter
  
  def build_subconscious_input(self, context: GPTPetContext) -> dict[str, Any]:
    return {'last_frame': self.sim_adapter.get_view()}
