from abc import ABC
from typing import Any

from gptpet_context import GPTPetContext
from module.base_module import BaseModule


class BaseSubconsciousInputModule(ABC):
  def build_conscious_input(self, context: GPTPetContext) -> dict[str, Any]:
    """ Build input needed for Conscious Modules
    from this SubConscious Module
    """
    pass