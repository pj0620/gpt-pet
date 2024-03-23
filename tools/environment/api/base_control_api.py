from abc import ABC, abstractmethod

from constants.motor import MOVE_RIGHT, MOVE_AHEAD, MOVE_LEFT, MOVE_BACK, ROTATE_LEFT
from model.objects import Object
from model.vision import PhysicalPassagewayInfo


class BaseControlAPI(ABC):
  last_steps: list[tuple[str, dict[str, float]]]
  
  def __init__(self):
    self.last_steps = []
    self.passageways: list[PhysicalPassagewayInfo] = []
    self.objects: list[Object] = []
    
  def update_passageways(self, new_passageways: list[PhysicalPassagewayInfo]):
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
  def goto_passageway(self, passageway_color: str) -> None:
    """
    :param passageway_color: color of passageway to move into
    """
  
  @abstractmethod
  def goto_object(self, object_name: str) -> None:
    """
    :param object_name: name of object to move towards
    """
  