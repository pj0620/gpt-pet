from typing import Any

from constants.motor import ROTATE_LEFT, MOVE_AHEAD
from gptpet_env import GPTPetEnv
from module.conscious.base_conscious_module import BaseConsciousModule

FIELD_OF_VISION = 90

class WalkForwardModule(BaseConsciousModule):
  def execute(self, env: GPTPetEnv) -> dict[str, Any]:
    turn_percent = env.subconscious_outputs['turn_percent']
    if -10 < turn_percent < 10:
      env.motor_service.do_movement(
        action=MOVE_AHEAD
      )
      return {
        "performed": {
          "movement": MOVE_AHEAD
        }
      }
    else:
      degrees = (turn_percent/100) * FIELD_OF_VISION / 2.0
      env.motor_service.do_rotate(
        action=ROTATE_LEFT,
        degrees=degrees
      )
      return {
        "performed": {
          "rotate": ROTATE_LEFT,
          "degrees": degrees
        }
      }
    
    