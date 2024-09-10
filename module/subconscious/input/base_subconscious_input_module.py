from abc import ABC, abstractmethod
from typing import Any

from gptpet_context import GPTPetContext
from model.subconscious import ConsciousInput
from module.base_module import BaseModule


class BaseSubconsciousInputModule(ABC):
  @abstractmethod
  def build_conscious_input(self, context: GPTPetContext) -> ConsciousInput:
    """
    Build input needed for Conscious Modules
    from this SubConscious Module
    :param context: GPTPet Context
    :return: tuple of output from this module
      (full output from this module, minified module to be passed to llm)
    """
    pass
