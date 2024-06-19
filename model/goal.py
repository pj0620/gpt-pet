from dataclasses import dataclass


@dataclass
class Goal:
  description: str
  completed: bool
  goal_id: str
  