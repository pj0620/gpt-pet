from abc import ABC
from typing import Any

from gptpet_env import GPTPetEnv


class BaseSensoryModule(ABC):
  
  def build_subconscious_input(self, env: GPTPetEnv) -> dict[str, Any]:
    """ Build input needed for Subconscious Modules
    from this Sensory Module
    """
    pass