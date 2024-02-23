from dataclasses import dataclass


@dataclass
class EnvironmentResult:
  successful: bool
  feedback: str
