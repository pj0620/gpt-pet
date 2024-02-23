from enum import Enum
from typing import Type, Optional, Any

from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool
from langchain_core.callbacks import CallbackManagerForToolRun

from constants.motor import ALL_MOTOR_ACTIONS
from service.motor.base_motor_adapter import BaseMotorAdapter
from tools.environment.api.base_control_api import BaseControlAPI
from tools.environment.api.mock_control_api import MockControlAPI
from tools.environment.model import EnvironmentInput


class MockEnvironmentTool(BaseTool):
  name = "mock_environment"
  description = ("mock environment to use for validating programs before running on the actual robot. Submit properly "
                 "formatted python programs to execute.")
  args_schema: Type[BaseModel] = EnvironmentInput
  control_api: BaseControlAPI
  
  def __init__(self):
    super(MockEnvironmentTool, self).__init__(control_api = MockControlAPI())
  
  
  def execute_python(self, code: str):
    control_api = self.control_api
    exec(code, {'control_api': control_api})
  
  def _run(
      self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
  ) -> str:
    print(f"MockEnvironmentTool running `{query}`")
    
    try:
      self.execute_python(query)
      return "success!"
    except Exception as e:
      return f"failed! got following exception: {e}"