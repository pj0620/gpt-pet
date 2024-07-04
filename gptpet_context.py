from typing import Any

from mixin.goal.base_goal_mixin import BaseGoalMixin
from model.conscious import TaskResult
from model.objects import Object
from model.passageway import Passageway
from model.subconscious import ConsciousInput
from model.vision import PetViewSource
from service.analytics_service import AnalyticsService
from service.device_io.base_device_io_adapter import BaseDeviceIOAdapter
from service.tilt_led.base_tilt_led_service import BaseTiltLedService
from service.motor.base_motor_adapter import BaseMotorAdapter
from service.vectordb_adapter_service import VectorDBAdapterService
from service.visual_llm_adapter_service import VisualLLMAdapterService


class GPTPetContext:
  vectordb_adapter: VectorDBAdapterService
  visual_llm_adapter: VisualLLMAdapterService
  motor_adapter: BaseMotorAdapter
  device_io_adapter: BaseDeviceIOAdapter
  led_service: Any
  led_tilt_service: BaseTiltLedService
  passageways: list[Passageway]
  objects_in_view: list[Object]
  analytics_service: AnalyticsService
  sensory_outputs: dict[str, Any]
  conscious_inputs: list[ConsciousInput]
  task_result: TaskResult
  
  # if a cached pet view was used this value is populated with its id
  last_pet_view: PetViewSource
  
  # additional mixins
  goal_mixin: BaseGoalMixin
