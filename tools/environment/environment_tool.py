import ast
import multiprocessing
import random
import threading
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
TIMEOUT_MESSAGE = "Execution terminated due to timeout."
SUCCESS_MESSAGE = "Executed successfully."

class EnvironmentTool(BaseTool):
  name = "environment_tool"
  description = ("this tool is used to test code to be run on the robot to make sure it works as well as get the special"
                 " passphrase for this code if it runs successfully. input must only be properly formatted python program.")
  args_schema: Type[BaseModel] = EnvironmentInput
  mock_control_api: BaseControlAPI
  real_control_api: BaseControlAPI
  
  def __init__(self,
               proximity_sensor_adapter: BaseProximitySensorAdapter,
               motor_adapter: BaseMotorAdapter):
    real_control_api = RealControlAPI(proximity_sensor_adapter, motor_adapter)
    super(EnvironmentTool, self).__init__(
      mock_control_api=MockControlAPI(),
      real_control_api=real_control_api
    )
  
  def real_execute(self, code: str):
    return exec(code, {"control_api": self.real_control_api})
  
  def mock_execute(self, code: str):
    return exec(code, {"control_api": self.mock_control_api})
  
  def contains_while_loop(self, code):
    try:
      tree = ast.parse(code)
      for node in ast.walk(tree):
        if isinstance(node, ast.While):
          return True
      return False
    except SyntaxError:
      # Handle code with syntax errors if necessary
      return False
  
  def _run(
      self, code: str, run_manager: Optional[CallbackManagerForToolRun] = None
  ) -> str:
    print(f"EnvironmentTool running `{code}`")
    
    if self.contains_while_loop(code):
      return "failed! code contains a while loop which is not allowed!"
    
    try:
      self.mock_execute(code)
    except Exception as e:
      return f"failed! got following exception when testing in mock, the program needs to be updated: {e}"
    
    try:
      self.real_execute(code)
    except Exception as e:
      return f"failed! got following exception when running on robot, the program needs to be updated: {e}"
    
    return "success! the secret passphrase this round is " + random.choice(secret_passphrases)