from dataclasses import dataclass


@dataclass(frozen=True)
class Object:
  horizontal_angle: float
  description: str
  name: str
