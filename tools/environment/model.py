from pydantic import BaseModel, Field


class EnvironmentInput(BaseModel):
  code: str = Field(
    description=f"properly formatted python program to run on the robot. Please include comments on "
                f"each line explaining how it helps complete the task"
  )
