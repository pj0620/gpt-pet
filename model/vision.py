from dataclasses import dataclass

import numpy as np
from pydantic.v1 import BaseModel, Field

from model.objects import ObjectDescription
from model.passageway import PassagewayDescriptionPydantic


@dataclass(frozen=True)
class CreatePetViewModel:
  image: str
  description: str
  passageway_descriptions: str
  objects_descriptions: str
  passageways: str
  
  
@dataclass(frozen=True)
class CreatePetViewWithGoalModel(CreatePetViewModel):
  goal_id: str


class PetViewDescription(BaseModel):
  description: str = Field(description="a text description of what gptpet is currently seeing")
  passageway_descriptions: list[PassagewayDescriptionPydantic] = (
    Field(description="list of descriptions for all passageways in gptpet's view"))
  objects_descriptions: list[ObjectDescription] = (
    Field(description="list of descriptions for all objects in gptpet's view"))


class NewTaskResponse(BaseModel):
  reasoning: str = Field(description="a text description of what gptpet is currently seeing")
  task: str = Field(description="task to execute")

@dataclass
class PetViewSource:
  pet_view_id: str
  newly_created: bool
