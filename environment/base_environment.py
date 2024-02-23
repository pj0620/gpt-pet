from abc import ABC

from environment.model import EnvironmentResult


class BaseEnvironment(ABC):
  def run_python_code(self, python_code: str) -> EnvironmentResult:
    """
    :param python_code: code to execute in the environment
    :return: EnvironmentResult describing the results of running python code
    """
    pass