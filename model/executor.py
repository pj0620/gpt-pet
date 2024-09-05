from pydantic.v1 import BaseModel, Field


class SkillValidationResponse(BaseModel):
  reasoning: str = Field(description="description of why this code does or does not solve the given task")
  solves_task: bool = Field(description="will skill code solve the task")
