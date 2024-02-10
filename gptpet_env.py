from typing import Any

from service.motor.base_motor_service import BaseMotorService
from service.vectordb_adapter_service import VectorDBAdapterService
from service.visual_llm_adapter_service import VisualLLMAdapterService


class GPTPetEnv:
    vectordb_adapter: VectorDBAdapterService
    visual_llm_adapter: VisualLLMAdapterService
    motor_service: BaseMotorService
    sensory_outputs: dict[str, Any]
    subconscious_outputs: dict[str, Any]
    