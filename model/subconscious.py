from dataclasses import dataclass
from typing import Any

@dataclass
class ConsciousInput:
  description: str
  value: dict[str, Any]
  schema: dict[str, Any]
  name: str
