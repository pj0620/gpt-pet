from abc import ABC
from typing import Any

from gptpet_env import GPTPetEnv


class BaseConsciousModule(ABC):
  def execute(self, env: GPTPetEnv) -> dict[str, Any]:
    """ update conscious mind
    """
    pass