from typing import Any

from constants.ai2thor import MOVEMENT_TO_AI2THOR_MOVEMENT, ROTATE_TO_AI2THOR_ROTATE
from service.motor.base_motor_service import BaseMotorService
from sim_adapter import SimAdapter


class Ai2ThorMotorService(BaseMotorService):
  def __init__(
      self,
      sim_adapter: SimAdapter
  ):
    self.sim_adapter = sim_adapter
  
  def do_movement(
      self,
      action: str,
      move_magnitude: float = None
  ) -> dict[str, Any]:
    assert action in MOVEMENT_TO_AI2THOR_MOVEMENT.keys(), f'invalid movement action {action}'
    
    self.sim_adapter.do_step(
      action=MOVEMENT_TO_AI2THOR_MOVEMENT[action],
      moveMagnitude=move_magnitude
    )
    
    return {
      "move_completed": action,
      "magnitude": move_magnitude
    }
  
  def do_rotate(
      self,
      action: str,
      degrees: float = None
  ) -> dict[str, Any]:
    assert action in ROTATE_TO_AI2THOR_ROTATE.keys(), f'invalid rotate action {action}'
    
    self.sim_adapter.do_step(
      action=ROTATE_TO_AI2THOR_ROTATE[action],
      degrees=degrees
    )
    
    return {
      "rotate_completed": action,
      "degrees": degrees
    }
