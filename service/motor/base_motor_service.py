from abc import ABC, abstractmethod
from typing import Any

from model.motor import MovementResult


class BaseMotorService(ABC):
  @abstractmethod
  def do_movement(
      self,
      action: str,
      move_magnitude: float = None
  ) -> MovementResult:
    """ move pet
    TODO: better description
    """
    pass
  
  @abstractmethod
  def do_rotate(
      self,
      action: str,
      degrees: float = None
  ) -> MovementResult:
    """ rotate pet
    TODO: better description
    """
    pass
  
  @abstractmethod
  def stop(self):
    """
    stops all motors
    """
    pass
  
  @abstractmethod
  def setup_motors(self):
    """
    setup motors, mostly gpio pinmodes, turn off motors by default
    """
    pass
