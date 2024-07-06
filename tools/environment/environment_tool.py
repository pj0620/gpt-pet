import ast
import random
from typing import Type, Optional

from langchain.pydantic_v1 import BaseModel
from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun

from gptpet_context import GPTPetContext
from model.objects import Object
from model.passageway import Passageway
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
  description = ("An expertly crafted environement to verify programs to be run on robots. Used for when you want to "
                 "write a program that controls a robot to complete a task. The input should be a valid python program")
  args_schema: Type[BaseModel] = EnvironmentInput
  mock_control_api: BaseControlAPI
  real_control_api: BaseControlAPI
  context: GPTPetContext
  
  def __init__(self,
               proximity_sensor_adapter: BaseDeviceIOAdapter,
               motor_adapter: BaseMotorAdapter,
               context: GPTPetContext):
    real_control_api = RealControlAPI(proximity_sensor_adapter, motor_adapter, context)
    super(EnvironmentTool, self).__init__(
      mock_control_api=MockControlAPI(),
      real_control_api=real_control_api,
      context=context
    )
    
  def update_passageways(self, passageways: list[Passageway]):
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
    
    if len(code) > 500:
      error_msg = "failed! code is greater than 500 characters"
      self.context.analytics_service.new_text("environmental_tool: " + error_msg)
      return error_msg
    
    if self.contains_while_loop(code):
      error_msg = "failed! code contains a while loop which is not allowed!"
      self.context.analytics_service.new_text("environmental_tool: " + error_msg)
      return error_msg
    
    try:
      self.mock_execute(code)
    except Exception as e:
      error_msg = f"failed! got following exception when testing in mock, the program needs to be updated: {e}"
      self.context.analytics_service.new_text("environmental_tool: " + error_msg)
      return error_msg
    
    self.real_control_api.clear_last_actions()
    try:
      self.real_execute(code)
    except Exception as e:
      error_msg = f"failed! got following exception when running on robot, the program needs to be updated: {e}"
      self.context.analytics_service.new_text("environmental_tool: " + error_msg)
      return error_msg
    
    return "success! the secret passphrase this round is " + random.choice(secret_passphrases)