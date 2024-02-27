from pydantic import BaseModel, Field


class EnvironmentInput(BaseModel):
  code: str = Field(description=f"properly formatted python program to run on the robot. Please include comments on each line explaining how it helps complete the task")
  reasoning: str = Field(description=f"reasoning behind why this program will help complete your task")
