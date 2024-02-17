from abc import ABC
from typing import Any

from gptpet_env import GPTPetEnv
from model.task import TaskDefinition


class BaseConsciousModule(ABC):
  def generate_new_task(self, env: GPTPetEnv) -> TaskDefinition:
    """ update conscious mind
    """
    pass