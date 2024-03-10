import os

import cv2
import numpy as np
from ai2thor.controller import Controller

from constants.ai2thor import AI2THOR_CROUCH, AI2THOR_NOOP
from constants.motor import MOVE_BACK, MOVE_LEFT, MOVE_RIGHT, MOVE_AHEAD
from model.collision import CollisionError
from utils.math_utils import get_rotation_vector, dict_to_array

WINDOW_NAME = 'Pet View'
PROXIMITY_SENSOR_MAX_STEPS = 10
PROXIMITY_SENSOR_RESOLUTION = 0.1

# cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

class SimAdapter:
  def __init__(self):
    self.controller = Controller(
      scene="FloorPlan2",
      gridSize=0.01,
      rotateStepDegrees=90,
      # camera properties
      # width=512,
      # height=512,
      width=1024,
      height=1024,
      fieldOfView=70,
      
      renderDepthImage=True
    )
    self.last_event = None
    self.controller.step(AI2THOR_CROUCH)
    self.noop()
    
    self.skip_proximity_sensors = os.environ.get('SIM_SKIP_PROXIMITY_SENSOR') == 'true'
    self.enable_ai2thor_debug_logging = os.environ.get('ENABLE_AI2THOR_DEBUG_LOGGING') == 'true'
    
    self.proximity_measurements = None
    self.update_proximity_sensors()
  
  def noop(self):
    self.last_event = self.controller.step(AI2THOR_NOOP)
  
  def do_step(self,
              action,
              update_proximity_sensors=True,
              **kwargs
  ):
    if self.enable_ai2thor_debug_logging: print(f'calling do_step with {action=}, {update_proximity_sensors=}, {kwargs=}')
    self.last_event = self.controller.step(action=action, **kwargs)
    if self.enable_ai2thor_debug_logging: print(f'{self.last_event=}')
    # self.update_camera()
    if update_proximity_sensors:
      if not self.last_event.metadata['lastActionSuccess']:
        raise CollisionError(f"hit something while executing {action} with following args {kwargs}")
      else:
        print(f"successfully executed {action} with following args {kwargs}")
      self.update_proximity_sensors()
    
  # def get_collision_direction(self):
  #   if self.last_event.metadata["lastActionSuccess"]:
  #     return None
  #
  #   blocking_object_name = self.last_event.metadata["errorMessage"].split(' is blocking Agent 0 from moving by ')[0].strip()
  #
  #   blocking_objects = [
  #     obj
  #     for obj in self.last_event.metadata["objects"]
  #     if obj["name"] == blocking_object_name
  #   ]
  #
  #   return 'ahead'
  
  def get_view(self):
    self.noop()
    last_frame = self.last_event.frame
    return last_frame
  
  def get_depth_view(self):
    self.noop()
    last_frame = self.last_event.depth_frame
    return last_frame
  
  def last_event_successful(self):
    if self.last_event is None:
      return False
    return self.last_event.metadata['lastActionSuccess']
  
  def update_proximity_sensors(self):
    actions = [MOVE_RIGHT, MOVE_AHEAD, MOVE_LEFT, MOVE_BACK]
    directions = ['right', 'ahead', 'left', 'back']
    
    start_position = dict(self.last_event.metadata["agent"]["position"])
    distances = {
      direction: float('inf')
      for direction in directions
    }
    if not self.skip_proximity_sensors:
      for action, direction in zip(actions, directions):
        self.noop()
        final_steps = 0
        
        jump_size = PROXIMITY_SENSOR_MAX_STEPS
        while jump_size > 0:
          self.do_step(
            action=action,
            moveMagnitude=PROXIMITY_SENSOR_RESOLUTION * jump_size,
            update_proximity_sensors=False
          )
          if self.last_event_successful():
            final_steps = jump_size
            break
          jump_size //= 2
        distances[direction] = final_steps * PROXIMITY_SENSOR_RESOLUTION
        self.do_step(
          action="Teleport",
          position=start_position,
          update_proximity_sensors=False
        )
      
    self.proximity_measurements = distances
      
