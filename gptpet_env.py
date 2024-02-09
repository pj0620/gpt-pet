from typing import Any

from service.vectordb_adapter_service import VectorDBAdapterService
from service.visual_llm_adapter_service import VisualLLMAdapterService


class GPTPetEnv:
    vectordb_adapter: VectorDBAdapterService
    visual_llm_adapter: VisualLLMAdapterService
    sensory_outputs: dict[str, Any]
    subconscious_outputs: dict[str, Any]
    