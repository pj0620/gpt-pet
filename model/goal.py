from dataclasses import dataclass


@dataclass
class Goal:
  description: str | None
  completed: bool
  