import warnings
from abc import ABC, abstractmethod

from constants.motor import MOVE_RIGHT, MOVE_AHEAD, MOVE_LEFT, MOVE_BACK, ROTATE_LEFT
from model.objects import Object
from model.passageway import Passageway


class BaseControlAPI(ABC):
  last_steps: list[tuple[str, dict[str, float]]]
  
  def __init__(self):
    self.last_steps = []
    self.passageways: list[Passageway] = []
    self.objects: list[Object] = []
    
  def update_passageways(self, new_passageways: list[Passageway]):
    self.passageways = new_passageways
    
  def update_objects(self, new_objects: list[Object]):
    self.objects = new_objects
  
  def push_new_action(self, action: str, params: dict[str, float]):
    print(f"push_new_action: {action} with {params}")
    self.last_steps.append((action, params))
  
  def clear_last_actions(self):
    self.last_steps = []
    
  def rollback_last_successful(self):
    print("failed, rolling back last actions")
    try:
      for action, params in self.last_steps[::-1]:
        for key in params:
          if params[key] is not None:
            params[key] = -1 * params[key]
        print(f"[ROLLBACK] executing {action} with {params}")
        if action == MOVE_RIGHT:
          self.move_right(**params)
        elif action == MOVE_AHEAD:
          self.move_ahead(**params)
        elif action == MOVE_LEFT:
          self.move_left(**params)
        elif action == MOVE_BACK:
          self.move_back(**params)
        elif action == ROTATE_LEFT:
          self.rotate(**params)
    except Exception as e:
      print("[ROLLBACK] got exception during rollback action, ", e)
    
  
  @abstractmethod
  def move_right(
      self,
      move_magnitude: float = None
  ) -> str:
    """
    :param move_magnitude: distance for robot to move
    :return: results of moving
    """
    pass
  
  @abstractmethod
  def move_ahead(
      self,
      move_magnitude: float = None
  ) -> str:
    """
    :param move_magnitude: distance for robot to move
    :return: results of moving
    """
    pass
  
  @abstractmethod
  def move_left(
      self,
      move_magnitude: float = None
  ) -> str:
    """
    :param move_magnitude: distance for robot to move
    :return: results of moving
    """
    pass
  
  @abstractmethod
  def move_back(
      self,
      move_magnitude: float = None
  ) -> str:
    """
    :param move_magnitude: distance for robot to move
    :return: results of moving
    """
    pass
  
  @abstractmethod
  def rotate(
      self,
      degrees: float = None
  ) -> str:
    """
    :param degrees: rough number of degrees for robot to turn
    :return: results of turning
    """
    pass
  
  @abstractmethod
  def read_right_sensor(
      self
  ) -> float:
    """
    :return: Approximate distance in meters from the robot to the nearest obstacle right of GPTPet.
    """
    pass
  
  @abstractmethod
  def read_ahead_sensor(
      self
  ) -> float:
    """
    :return: Approximate distance in meters from the robot to the nearest obstacle ahead of GPTPet.
    """
    pass
  
  @abstractmethod
  def read_left_sensor(
      self
  ) -> float:
    """
    :return: Approximate distance in meters from the robot to the nearest obstacle left of GPTPet.
    """
    pass
  
  @abstractmethod
  def read_back_sensor(
      self
  ) -> float:
    """
    :return: Approximate distance in meters from the robot to the nearest obstacle to back of GPTPet.
    """
    pass
  
  @abstractmethod
  def goto_passageway(self, passageway_name: str) -> None:
    """
    :param passageway_name: color of passageway to move into
    """
    
  def get_passageway(self, passageway_name: str) -> Passageway:
    """
    :param passageway_name: name of passageway to get
    :return: matching passageway, if not found throws an error
    """
    matching_passageways = [p for p in self.passageways if p.name == passageway_name]
    if len(matching_passageways) == 0:
      raise Exception(f"failed to move down `{passageway_name}` passageway. Does not exist. The only valid passageways "
                      f"are {[p.name for p in self.passageways]}")
    elif len(matching_passageways) > 1:
      warnings.warn(f"found multiple passageways with the same color {passageway_name} choosing first")
  
    return matching_passageways[0]
  
  @abstractmethod
  def goto_object(self, object_name: str) -> None:
    """
    :param object_name: name of object to move towards
    """
  