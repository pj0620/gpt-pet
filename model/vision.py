from dataclasses import dataclass

import numpy as np
from pydantic.v1 import BaseModel, Field


@dataclass
class PhysicalPassagewayInfo:
  color: str
  turn_degrees: float


@dataclass
class LabelPassagewaysResponse:
  # final image including Xs in passageways
  final_image: np.array
  
  # color of each x
  xs_info: list[PhysicalPassagewayInfo]

@dataclass(frozen=True)
class CreatePetViewModel:
  image: str
  description: str
  passageway_descriptions: str
  passageways: str


class PassagewayDescription(BaseModel):
  color: str = Field(description="color of x denoting this passageway")
  description: str = Field(description="a text of what this passageway leads too")


class PetViewDescription(BaseModel):
  description: str = Field(description="a text description of what gptpet is currently seeing")
  passageway_descriptions: list[PassagewayDescription] = (
    Field(description="list of descriptions for all passageways in gptpet's view"))

class NewTaskResponse(BaseModel):
  reasoning: str = Field(description="a text description of what gptpet is currently seeing")
  task: str = Field(description="task to execute")