import random
from enum import Enum
from typing import Type, Optional, Any

from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool
from langchain_core.callbacks import CallbackManagerForToolRun

from constants.motor import ALL_MOTOR_ACTIONS
from service.motor.base_motor_adapter import BaseMotorAdapter
from service.sensor.base_proximity_sensor_adapter import BaseProximitySensorAdapter
from tools.environment.api.base_control_api import BaseControlAPI
from tools.environment.api.mock_control_api import MockControlAPI
from tools.environment.api.real_control_api import RealControlAPI
from tools.environment.model import EnvironmentInput


secret_passphrases = ["apple", "orange", "banana"]

class EnvironmentTool(BaseTool):
  name = "environment_tool"
  description = ("this tool is used to test code to be run on the robot, and then run the code on the actual robot. "
                 "Results are collected and sent back as feedback. Submit properly formatted python programs to execute"
                 "Once a valid program is executed, a secret passphrase is returned")
  args_schema: Type[BaseModel] = EnvironmentInput
  mock_control_api: BaseControlAPI
  real_control_api: BaseControlAPI
  
  def __init__(
      self,
      proximity_sensor_adapter: BaseProximitySensorAdapter,
      motor_adapter: BaseMotorAdapter
  ):
    real_control_api = RealControlAPI(
      proximity_sensor_adapter=proximity_sensor_adapter,
      motor_adapter=motor_adapter
    )
    super(EnvironmentTool, self).__init__(
      mock_control_api=MockControlAPI(),
      real_control_api=real_control_api
    )
  
  def real_execute(self, code: str):
    exec(code, {'control_api': self.real_control_api})
    
  def mock_execute(self, code: str):
    exec(code, {'control_api': self.mock_control_api})
  
  def _run(
      self, code: str, reasoning: str, run_manager: Optional[CallbackManagerForToolRun] = None
  ) -> str:
    print(f"EnvironmentTool running `{code}` with following reasoning: {reasoning}")
    
    try:
      self.mock_execute(code)
    except Exception as e:
      return f"failed! got following exception when testing in mock, the program needs to be updated: {e}"
    
    try:
      self.real_execute(code)
    except Exception as e:
      return f"failed! got following exception when running on robot, the program needs to be updated: {e}"
    
    return "success! the secret passphrase this round is " + random.choice(secret_passphrases)