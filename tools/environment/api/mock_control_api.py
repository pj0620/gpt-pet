import warnings
from abc import ABC

from constants.motor import MOVE_RIGHT, MOVE_AHEAD, MOVE_LEFT, MOVE_BACK, ROTATE_RIGHT
from model.motor import MovementResult
from tools.environment.api.base_control_api import BaseControlAPI


class MockControlAPI(BaseControlAPI):
  def move_right(
      self,
      move_magnitude: float = None
  ) -> MovementResult:
    print("MockControlAPI: executing move_right")
    return MovementResult(
      successful=True,
      action=MOVE_RIGHT,
      move_magnitude=move_magnitude
    )
  
  def move_ahead(
      self,
      move_magnitude: float = None
  ) -> MovementResult:
    print("MockControlAPI: executing move_ahead")
    return MovementResult(
      successful=True,
      action=MOVE_AHEAD,
      move_magnitude=move_magnitude
    )
  
  def move_left(
      self,
      move_magnitude: float = None
  ) -> MovementResult:
    print("MockControlAPI: executing move_left")
    return MovementResult(
      successful=True,
      action=MOVE_LEFT,
      move_magnitude=move_magnitude
    )
  
  def move_back(
      self,
      move_magnitude: float = None
  ) -> MovementResult:
    print("MockControlAPI: executing move_back")
    return MovementResult(
      successful=True,
      action=MOVE_BACK,
      move_magnitude=move_magnitude
    )
  
  def rotate(
      self,
      degrees: float = None
  ) -> MovementResult:
    print("MockControlAPI: executing rotate")
    return MovementResult(
      successful=True,
      action=ROTATE_RIGHT,
      degrees=degrees
    )
  
  def read_right_sensor(
      self
  ) -> float:
    print("MockControlAPI: reading right sensor")
    return 100.0
  
  def read_ahead_sensor(
      self
  ) -> float:
    print("MockControlAPI: reading ahead sensor")
    return 100.0
  
  def read_left_sensor(
      self
  ) -> float:
    print("MockControlAPI: reading left sensor")
    return 100.0
  
  def read_back_sensor(
      self
  ) -> float:
    print("MockControlAPI: reading back sensor")
    return 100.0
  
  def goto_passageway(
      self, passageway_name: str
  ) -> str:
    print(f"MockControlAPI: going down '{passageway_name}' passageway")
    self.get_passageway(passageway_name)
    return "success!"
  
  def goto_object(self, object_name: str) -> str:
    print(f"MockControlAPI: going to object `{object_name}`")
    matching_objects = [p for p in self.objects if p.name.lower() == object_name.lower()]
    if len(matching_objects) == 0:
      raise Exception(f"failed to move toward object `{object_name}`. Does not exist. The only valid objects "
                      f"are {self.objects}")
    elif len(matching_objects) > 1:
      warnings.warn(f"found multiple objects with the same name {object_name} choosing first")
      
    return "success!"
