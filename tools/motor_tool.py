from enum import Enum
from typing import Type, Optional, Any

from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool
from langchain_core.callbacks import CallbackManagerForToolRun

from constants.motor import ALL_MOTOR_ACTIONS
from service.motor.base_motor_adapter import BaseMotorAdapter

class MovementInput(BaseModel):
  movement: str = Field(description=f"movement for robot to perform, must be in the following list: {ALL_MOTOR_ACTIONS}")

class MotorTool(BaseTool):
  name = "motor_control"
  description = "used to control robot's motors"
  args_schema: Type[BaseModel] = MovementInput
  motor_service: BaseMotorAdapter
  
  def __init__(self, motor_service: BaseMotorAdapter, **kwargs: Any):
    super(MotorTool, self).__init__(motor_service=motor_service)
    self.motor_service = motor_service
  
  def _run(
      self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
  ) -> str:
    if query not in ALL_MOTOR_ACTIONS:
      return  f"invalid action, must be in the following list: {ALL_MOTOR_ACTIONS}"
    self.motor_service.do_action(query)