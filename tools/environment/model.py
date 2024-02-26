from pydantic import BaseModel, Field


class EnvironmentInput(BaseModel):
  program: str = Field(
    description=f"python program to run on the robot")

