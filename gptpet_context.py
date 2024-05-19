from dataclasses import dataclass
from typing import Any

from model.conscious import TaskResult
from model.objects import Object
from model.subconscious import ConsciousInput
from model.vision import PhysicalPassagewayInfo
from service.analytics_service import AnalyticsService
from service.device_io.base_device_io_adapter import BaseDeviceIOAdapter
from service.motor.base_motor_adapter import BaseMotorAdapter
from service.vectordb_adapter_service import VectorDBAdapterService
from service.visual_llm_adapter_service import VisualLLMAdapterService

@dataclass
class ActionContext:
  sensory_outputs: dict[str, Any]
  conscious_inputs: list[ConsciousInput]
  task_result: TaskResult
  
@dataclass
class GPTPetContext(ActionContext):
  vectordb_adapter: VectorDBAdapterService
  visual_llm_adapter: VisualLLMAdapterService
  motor_adapter: BaseMotorAdapter
  device_io_adapter: BaseDeviceIOAdapter
  passageways: list[PhysicalPassagewayInfo]
  objects_in_view: list[Object]
  analytics_service: AnalyticsService
  
  def get_action_context(self) -> ActionContext:
    return ActionContext(
      sensory_outputs=self.sensory_outputs,
      conscious_inputs=self.conscious_inputs,
      task_result=self.task_result
    )