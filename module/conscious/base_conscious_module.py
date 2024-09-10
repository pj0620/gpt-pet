from abc import ABC, abstractmethod
from typing import Any

from gptpet_context import GPTPetContext
from model.conscious import TaskDefinition, TaskResult


class BaseConsciousModule(ABC):
  @abstractmethod
  def generate_new_task(self, context: GPTPetContext) -> TaskDefinition:
    """ update conscious mind
    """
    pass
  
  @abstractmethod
  def report_task_result(self, task_definition: TaskDefinition, task_result: TaskResult) -> None:
    """ update task results for success or fail
    """
    pass
