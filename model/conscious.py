from dataclasses import dataclass

from pydantic.v1 import Field, BaseModel


class NewTaskResponse(BaseModel):
  reasoning: str = Field(description="description of why this task should be executed")
  task: str = Field(description="task to execute")
  
  
class NewTaskResponseGoalIncluded(NewTaskResponse):
  next_goal: str = Field(description="next goal for gptpet")
  previous_goal_completed: bool = Field(description="was previous goal completed")


@dataclass
class TaskDefinition:
  input: str
  reasoning: str
  task: str


@dataclass
class TaskResult:
  success: bool
  executor_output: str
  
  
@dataclass
class SavedTask:
  task: str
  reasoning: str
  pet_view_id: str
  
