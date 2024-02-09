from dataclasses import dataclass


@dataclass(frozen=True)
class PetView:
  image: str
  description: str
  pass