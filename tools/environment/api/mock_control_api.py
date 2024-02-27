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
      degress: float = None
  ) -> MovementResult:
    print("MockControlAPI: executing rotate")
    return MovementResult(
      successful=True,
      action=ROTATE_RIGHT,
      degrees=degress
    )
  
  def read_right_sensor(
      self
  ) -> float:
    return 100.0
  
  def read_ahead_sensor(
      self
  ) -> float:
    return 100.0
  
  def read_left_sensor(
      self
  ) -> float:
    return 100.0
  
  def read_back_sensor(
      self
  ) -> float:
    return 100.0