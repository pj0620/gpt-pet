from environment.base_environment import BaseEnvironment
from environment.model import EnvironmentResult


class MockEnvironment(BaseEnvironment):
  def run_python_code(self, python_code: str) -> EnvironmentResult:
    return EnvironmentResult(
      successful=True,
      feedback="no issues"
    )
