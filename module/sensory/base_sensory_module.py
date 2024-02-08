from abc import ABC
from typing import Any


class BaseSensoryModule(ABC):
  
  def build_subconscious_input(self) -> None:
    """ Build input needed for Subconscious Modules
    from this Sensory Module
    """
    pass