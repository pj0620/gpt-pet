from abc import ABC
from typing import Any

from gptpet_env import GPTPetEnv
from module.base_module import BaseModule


class BaseSubconsciousInputModule(ABC):
  def build_conscious_input(self, env: GPTPetEnv) -> dict[str, Any]:
    """ Build input needed for Conscious Modules
    from this SubConscious Module
    """
    pass