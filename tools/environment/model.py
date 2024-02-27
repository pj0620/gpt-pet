from pydantic import BaseModel, Field


class EnvironmentInput(BaseModel):
  code: str = Field(
    description=f"python program to run on the robot")

