from dataclasses import dataclass

from pydantic.v1 import Field, BaseModel


class NewTaskResponse(BaseModel):
  reasoning: str = Field(description="description of why this task should be executed")
  task: str = Field(description="task to execute")


@dataclass
class TaskDefinition:
  input: str
  reasoning: str
  task: str


@dataclass
class TaskResult:
  success: bool
  final_code: str