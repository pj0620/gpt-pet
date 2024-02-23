from abc import ABC

from model.motor import MovementResult


class BaseControlAPI(ABC):
  def move_right(
      self,
      move_magnitude: float = None
  ) -> MovementResult:
    """
    :param move_magnitude: distance for robot to move
    :return: results of moving
    """
    pass
  
  def move_ahead(
      self,
      move_magnitude: float = None
  ) -> MovementResult:
    """
    :param move_magnitude: distance for robot to move
    :return: results of moving
    """
    pass
  
  def move_left(
      self,
      move_magnitude: float = None
  ) -> MovementResult:
    """
    :param move_magnitude: distance for robot to move
    :return: results of moving
    """
    pass
  
  def move_back(
      self,
      move_magnitude: float = None
  ) -> MovementResult:
    """
    :param move_magnitude: distance for robot to move
    :return: results of moving
    """
    pass
  
  def rotate(
      self,
      degress: float = None
  ) -> MovementResult:
    """
    :param degress: rough number of degrees for robot to turn
    :return: results of turning
    """
    pass