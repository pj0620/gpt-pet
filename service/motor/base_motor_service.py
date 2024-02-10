from abc import ABC
from typing import Any


class BaseMotorService(ABC):
  def do_movement(
      self,
      action: str,
      move_magnitude: float = None
  ) -> dict[str, Any]:
    """ move pet
    TODO: better description
    """
    pass
  
  def do_rotate(
      self,
      action: str,
      degrees: float = None
  ) -> dict[str, Any]:
    """ rotate pet
    TODO: better description
    """
    pass
  