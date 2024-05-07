from typing import Any

from constants.ai2thor import MOVEMENT_TO_AI2THOR_MOVEMENT, ROTATE_TO_AI2THOR_ROTATE
from model.motor import MovementResult
from service.motor.base_motor_adapter import BaseMotorAdapter
from service.sim_adapter import SimAdapter


class Ai2ThorMotorService(BaseMotorAdapter):
  def __init__(
      self,
      sim_adapter: SimAdapter
  ):
    self.sim_adapter = sim_adapter
  
  def do_movement(
      self,
      action: str,
      move_magnitude: float = 1
  ) -> MovementResult:
    assert action in MOVEMENT_TO_AI2THOR_MOVEMENT.keys(), f'invalid movement action {action}'

    self.sim_adapter.do_step(
      action=MOVEMENT_TO_AI2THOR_MOVEMENT[action],
      moveMagnitude=move_magnitude
    )

    if self.sim_adapter.last_event_successful():
      return MovementResult(
        successful=True,
        action=action,
        move_magnitude=move_magnitude
      )
    else:
      return MovementResult(
        successful=False,
        action=action,
      )

  def do_rotate(
      self,
      action: str,
      degrees: float = None
  ) -> MovementResult:
    assert action in ROTATE_TO_AI2THOR_ROTATE.keys(), f'invalid rotate action {action}'

    self.sim_adapter.do_step(
      action=ROTATE_TO_AI2THOR_ROTATE[action],
      degrees=degrees
    )

    if self.sim_adapter.last_event_successful():
      return MovementResult(
        successful=True,
        action=action,
        degrees=degrees
      )
    else:
      return MovementResult(
        successful=False,
        action=action,
      )
    
  def stop(self):
    print("Ai2ThorMotorService: stop called")
    
  def setup_motors(self):
    print("Ai2ThorMotorService: setup_motors called")