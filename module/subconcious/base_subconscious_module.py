from abc import ABC
from typing import Any


class BaseSubconsciousModule(ABC):
  def build_subconscious_input(self) -> dict[str, Any]:
    """ Build input needed for Conscious Modules
    from this SubConscious Module
    """
    pass