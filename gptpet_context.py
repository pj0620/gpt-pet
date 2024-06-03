from typing import Any

from model.conscious import TaskResult
from model.objects import Object
from model.passageway import Passageway
from model.subconscious import ConsciousInput
from service.analytics_service import AnalyticsService
from service.device_io.base_device_io_adapter import BaseDeviceIOAdapter
from service.motor.base_motor_adapter import BaseMotorAdapter
from service.vectordb_adapter_service import VectorDBAdapterService
from service.visual_llm_adapter_service import VisualLLMAdapterService


class GPTPetContext:
  vectordb_adapter: VectorDBAdapterService
  visual_llm_adapter: VisualLLMAdapterService
  motor_adapter: BaseMotorAdapter
  device_io_adapter: BaseDeviceIOAdapter
  passageways: list[Passageway]
  objects_in_view: list[Object]
  analytics_service: AnalyticsService
  sensory_outputs: dict[str, Any]
  conscious_inputs: list[ConsciousInput]
  task_result: TaskResult