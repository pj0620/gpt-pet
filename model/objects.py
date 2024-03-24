from dataclasses import dataclass
  
@dataclass(frozen=True)
class ObjectCreateModel:
  object_description: str
  object_name: str
  
@dataclass(frozen=True)
class ObjectQueryModel:
  description: str
  name: str
  
@dataclass(frozen=True)
class ObjectResponseModel:
  description: str
  name: str


@dataclass
class Object:
  horizontal_angle: float
  object_distance: float
  description: str
  name: str
  seen_before: bool
  
  def get_query_model(self) -> ObjectQueryModel:
    return ObjectQueryModel(
      description=self.description,
      name=self.name
    )
  
  def get_create_model(self) -> ObjectCreateModel:
    return ObjectCreateModel(
      object_description=self.description,
      object_name=self.name
    )
