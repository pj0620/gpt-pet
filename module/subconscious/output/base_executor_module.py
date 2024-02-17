from abc import ABC
from typing import Any

from gptpet_env import GPTPetEnv
from model.task import TaskDefinition, TaskResult


class BaseExecutorModule(ABC):
  def execute(self, env: GPTPetEnv, new_task: TaskDefinition) -> TaskResult:
    """ Build input needed for Conscious Modules
    from this SubConscious Module
    """
    pass