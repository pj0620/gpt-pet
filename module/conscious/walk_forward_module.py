from typing import Any

from constants.motor import ROTATE_LEFT, MOVE_AHEAD
from gptpet_context import GPTPetContext
from model.conscious import TaskDefinition
from module.conscious.base_conscious_module import BaseConsciousModule

FIELD_OF_VISION = 90

class WalkForwardModule(BaseConsciousModule):
  def __init__(self):
    self.last_degrees = 0
  
  def generate_new_task(self, context: GPTPetContext) -> TaskDefinition:
    performed = []
    turn_percent = context.subconscious_outputs['turn_percent']
    fixed_loop = False
    failed = False
    # if turn_percent < -9 or turn_percent > 9:
    if False:
      degrees = (turn_percent / 100) * FIELD_OF_VISION
      result = context.motor_adapter.do_rotate(
        action=ROTATE_LEFT,
        degrees=degrees
      )
      performed = [{
        "rotate": ROTATE_LEFT,
        "degrees": degrees
      }]
      
      if degrees * self.last_degrees < 0:
        result = context.motor_adapter.do_movement(
          action=MOVE_AHEAD,
          move_magnitude=0.2
        )
        performed += [
          {
            "info": "found loop moving forward to break"
          },
          {
            "action": MOVE_AHEAD
          }
        ]
        fixed_loop = True
      self.last_degrees = degrees
    
    else:
      result = context.motor_adapter.do_movement(
        action=MOVE_AHEAD,
        move_magnitude=0.15
      )
      performed += [{
        "action": MOVE_AHEAD
      }]
      self.last_degrees = 0
      
    # if not result.successful:
    #   if fixed_loop:
    #     performed += [
    #       {
    #         "info": "moving forward did not break loop, turning around"
    #       },
    #       {
    #       "rotate": ROTATE_LEFT,
    #       "degrees": 180
    #     }]
    #     context.motor_service.do_rotate(
    #       action=ROTATE_LEFT,
    #       degrees=180
    #     )
    #   else:
    #     if 'vectordb_petview_id' not in context.subconscious_outputs:
    #       raise Exception(f'movement failed, but context.subconscious_outputs is not set. Please think of something else for me to do')
    #     pet_view_used_id = context.subconscious_outputs['vectordb_petview_id']
    #     print('action failed, deleting pet_view with following id: ', pet_view_used_id)
    #     context.vectordb_adapter.delete_pet_view(pet_view_used_id)
    #     failed = True
    
    print({
      "performed": performed,
      "failed": failed
    })
    
    return TaskDefinition('null', 'null')
    