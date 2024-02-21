from typing import Any

from model.subconscious import ConsciousInput
from service.motor.base_motor_service import BaseMotorService
from service.vectordb_adapter_service import VectorDBAdapterService
from service.visual_llm_adapter_service import VisualLLMAdapterService


class GPTPetContext:
    vectordb_adapter: VectorDBAdapterService
    visual_llm_adapter: VisualLLMAdapterService
    motor_service: BaseMotorService
    sensory_outputs: dict[str, Any]
    conscious_inputs: list[ConsciousInput]
    