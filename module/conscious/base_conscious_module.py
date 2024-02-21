from abc import ABC
from typing import Any

from gptpet_context import GPTPetContext
from model.task import TaskDefinition


class BaseConsciousModule(ABC):
  def generate_new_task(self, context: GPTPetContext) -> TaskDefinition:
    """ update conscious mind
    """
    pass