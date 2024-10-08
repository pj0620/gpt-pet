from abc import ABC, abstractmethod
from typing import Any

from gptpet_context import GPTPetContext
from model.conscious import TaskDefinition, TaskResult


class BaseExecutorModule(ABC):
  @abstractmethod
  def execute(self, context: GPTPetContext, new_task: TaskDefinition) -> TaskResult:
    """ Build input needed for Conscious Modules
    from this SubConscious Module
    """
    pass
