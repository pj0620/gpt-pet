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
from tools.environment.api.prod_control_api import ProdControlAPI
from tools.environment.model import EnvironmentInput


class ProdEnvironmentTool(BaseTool):
  name = "prod_environment"
  description = ("prod environment to use for executing programs on the actual robot. Submit properly "
                 "formatted python programs to execute, will return if actions are successful or failed")
  args_schema: Type[BaseModel] = EnvironmentInput
  control_api: BaseControlAPI
  
  def __init__(
      self,
      proximity_sensor_adapter: BaseProximitySensorAdapter,
      motor_adapter: BaseMotorAdapter
  ):
    control_api = ProdControlAPI(
      proximity_sensor_adapter=proximity_sensor_adapter,
      motor_adapter=motor_adapter
    )
    super(ProdEnvironmentTool, self).__init__(control_api=control_api)
  
  def execute_python(self, code: str):
    control_api = self.control_api
    exec(code, {'control_api': control_api})
  
  def _run(
      self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
  ) -> str:
    print(f"ProdEnvironmentTool running `{query}`")
    
    try:
      self.execute_python(query)
      return "success!"
    except Exception as e:
      return f"failed! got following exception: {e}"