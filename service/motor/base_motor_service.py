from abc import ABC
from typing import Any

from model.motor import MovementResult


class BaseMotorService(ABC):
  def do_movement(
      self,
      action: str,
      move_magnitude: float = None
  ) -> MovementResult:
    """ move pet
    TODO: better description
    """
    pass
  
  def do_rotate(
      self,
      action: str,
      degrees: float = None
  ) -> MovementResult:
    """ rotate pet
    TODO: better description
    """
    pass
  