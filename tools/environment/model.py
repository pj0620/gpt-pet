from pydantic import BaseModel, Field


class EnvironmentInput(BaseModel):
  program: str = Field(
    description=f"python program to be tested that will later be used to control the robot")

