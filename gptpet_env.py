from typing import Any

from service.vectordb_adapter_service import VectorDBAdapterService


class GPTPetEnv:
    vectordb_adapter_service: VectorDBAdapterService
    sensory_outputs: dict[str, Any]
    subconscious_outputs: dict[str, Any]
    