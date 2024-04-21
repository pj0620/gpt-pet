from typing import Any

from model.objects import Object
from model.subconscious import ConsciousInput
from model.vision import PhysicalPassagewayInfo
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
    sensory_outputs: dict[str, Any]
    conscious_inputs: list[ConsciousInput]
    passageways: list[PhysicalPassagewayInfo]
    objects_in_view: list[Object]
    analytics_service: AnalyticsService
    