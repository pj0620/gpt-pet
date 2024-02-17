from dataclasses import dataclass


@dataclass
class TaskDefinition:
  description: str
  name: str
  
@dataclass
class TaskResult:
  success: bool