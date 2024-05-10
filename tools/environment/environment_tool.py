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
from gptpet_context import GPTPetContext
from model.objects import Object
from model.vision import PhysicalPassagewayInfo
from service.device_io.base_device_io_adapter import BaseDeviceIOAdapter
from service.motor.base_motor_adapter import BaseMotorAdapter
from tools.environment.api.base_control_api import BaseControlAPI
from tools.environment.api.mock_control_api import MockControlAPI
from tools.environment.api.real_control_api import RealControlAPI
from tools.environment.model import EnvironmentInput

secret_passphrases = ["apple"]
TIMEOUT_MESSAGE = "Execution terminated due to timeout."
SUCCESS_MESSAGE = "Executed successfully."

class EnvironmentTool(BaseTool):
  name = "environment_tool"
  description = ("An expertly crafted environement to verify programs to be run on robots. Used for when you want to write a program that controls a robot to complete a task. The input should be a valid python program")
  args_schema: Type[BaseModel] = EnvironmentInput
  mock_control_api: BaseControlAPI
  real_control_api: BaseControlAPI
  
  def __init__(self,
               proximity_sensor_adapter: BaseDeviceIOAdapter,
               motor_adapter: BaseMotorAdapter,
               context: GPTPetContext):
    real_control_api = RealControlAPI(proximity_sensor_adapter, motor_adapter)
    super(EnvironmentTool, self).__init__(
      mock_control_api=MockControlAPI(),
      real_control_api=real_control_api
    )
    
  def update_passageways(self, passageways: list[PhysicalPassagewayInfo]):
    self.mock_control_api.update_passageways(passageways)
    self.real_control_api.update_passageways(passageways)
    
  def update_objects(self, passageways: list[Object]):
    self.mock_control_api.update_objects(passageways)
    self.real_control_api.update_objects(passageways)
  
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
    
    self.real_control_api.clear_last_actions()
    try:
      self.real_execute(code)
    except Exception as e:
      self.real_control_api.rollback_last_successful()
      return f"failed! got following exception when running on robot, the program needs to be updated: {e}"
    
    return "success! the secret passphrase this round is " + random.choice(secret_passphrases)