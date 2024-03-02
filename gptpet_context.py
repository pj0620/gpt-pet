from typing import Any

from model.subconscious import ConsciousInput
from service.motor.base_motor_adapter import BaseMotorAdapter
from service.sensor.base_proximity_sensor_adapter import BaseProximitySensorAdapter
from service.vectordb_adapter_service import VectorDBAdapterService
from service.vision_llm.base_visual_llm_adapter_service import BaseVisualLLMAdapterService


class GPTPetContext:
    vectordb_adapter: VectorDBAdapterService
    visual_llm_adapter: BaseVisualLLMAdapterService
    motor_adapter: BaseMotorAdapter
    proximity_sensor_adapter: BaseProximitySensorAdapter
    sensory_outputs: dict[str, Any]
    conscious_inputs: list[ConsciousInput]
    