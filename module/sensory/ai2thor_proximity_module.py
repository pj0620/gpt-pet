from typing import Any

from PIL import Image

from gptpet_env import GPTPetEnv
from module.sensory.base_sensory_module import BaseSensoryModule
from service.sim_adapter import SimAdapter


class Ai2ThorProximityModule(BaseSensoryModule):
  def __init__(
      self,
      sim_adapter: SimAdapter
  ):
    self.sim_adapter = sim_adapter
    self.last_event = None
  
  def build_subconscious_input(self, env: GPTPetEnv) -> dict[str, Any]:
    return {'proximity_measurements': self.sim_adapter.proximity_measurements()}
