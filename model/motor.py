from dataclasses import dataclass


@dataclass
class MovementResult:
  successful: bool
  action: str
  move_magnitude: float = None
  degrees: float = None
  
  