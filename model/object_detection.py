from dataclasses import dataclass


@dataclass(frozen=True)
class FoundObject:
  bbox: tuple[int, ...]
  class_name: str
  probability: float
  index: int
  