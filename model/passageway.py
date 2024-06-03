from dataclasses import dataclass
from pydantic.v1 import BaseModel, Field

import numpy as np


@dataclass
class HasColor:
  color: str


@dataclass
class PhysicalPassagewayInfo(HasColor):
  turn_degrees: float


# Note: two PassagewayDescription objects [PassagewayDescription, PassagewayDescriptionPydantic] are needed for the two
# purposes below
#     PassagewayDescription -> dataclass
#                           -> required to serialize/deserialize data into vectordb
#     PassagewayDescriptionPydantic
#                           -> Pydantic object
#                           -> required for PydanticParser provided by Langchain

@dataclass
class PassagewayDescription(HasColor):
  description: str
  name: str


class PassagewayDescriptionPydantic(BaseModel):
  color: str = Field(description="color of x denoting this passageway")
  description: str = Field(description="a text of what this passageway leads too")
  name: str = Field(description="a text of what this passageway leads too")


@dataclass
class Passageway(PassagewayDescription, PhysicalPassagewayInfo):
  pass
  
  
@dataclass
class LabelPassagewaysResponse:
  # final image including Xs in passageways
  final_image: np.array
  
  # color of each x
  xs_info: list[PhysicalPassagewayInfo]
