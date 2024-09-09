from abc import ABC, abstractmethod
from typing import Any

from gptpet_context import GPTPetContext


class BaseSensoryModule(ABC):
  
  @abstractmethod
  def build_subconscious_input(self, context: GPTPetContext) -> dict[str, Any]:
    """ Build input needed for Subconscious Modules
    from this Sensory Module
    """
    pass
