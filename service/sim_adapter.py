import cv2
import numpy as np
from ai2thor.controller import Controller

from constants.ai2thor import AI2THOR_CROUCH, AI2THOR_NOOP
from constants.motor import MOVE_BACK, MOVE_LEFT, MOVE_RIGHT, MOVE_AHEAD
from utils.math_utils import get_rotation_vector, dict_to_array

WINDOW_NAME = 'Pet View'
PROXIMITY_SENSOR_MAX_STEPS = 10
PROXIMITY_SENSOR_RESOLUTION = 0.1

cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

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
      # fieldOfView=90,
      
      renderDepthImage=True
    )
    self.controller.step(AI2THOR_CROUCH)
    self.controller.step(
      action='AddThirdPartyCamera',
      rotation=dict(x=0, y=0, z=0),
      position=dict(x=0, y=1, z=0),
      fieldOfView=90
    )
    self.noop()
    
    self.proximity_measurements = None
    self.update_proximity_sensors()
  
  def noop(self):
    self.last_event = self.controller.step(AI2THOR_NOOP)
    self.update_camera()
    
  def update_camera(self):
    pos = self.last_event.metadata["agent"]["position"]
    rot = self.last_event.metadata["agent"]["rotation"]
    
    # pos_arr = np.array([pos['x'], pos['y'], pos['z']])
    # camera_offset = np.array([0, 0, 0])
    # camera_pos_arr = pos_arr + camera_offset
    camera_pos = dict(
      x=pos['x'],
      y=pos['y'] + 1,
      z=pos['z']
    )
    camera_rot = dict(
      x=rot['x'] + 90,
      y=rot['y'],
      z=rot['z']
    )
    
    self.controller.step(
      action="UpdateThirdPartyCamera",
      thirdPartyCameraId=0,
      position=camera_pos,
      rotation=camera_rot
    )
  
  def do_step(self,
              action,
              update_proximity_sensors=True,
              **kwargs
  ):
    print(f'calling do_step with {action=}, {update_proximity_sensors=}, {kwargs=}')
    self.last_event = self.controller.step(action=action, **kwargs)
    print(f'{self.last_event=}')
    self.update_camera()
    if update_proximity_sensors:
      self.update_proximity_sensors()
  
  def get_view(self):
    self.noop()
    third_party_last_frame = self.last_event.third_party_camera_frames[0]
    # third_party_last_frame = self.last_event.depth_frame
    last_frame = self.last_event.frame
    cv2.imshow(WINDOW_NAME, third_party_last_frame)
    cv2.waitKey(33)
    return last_frame
  
  def last_event_successful(self):
    if self.last_event is None:
      return False
    return self.last_event.metadata['lastActionSuccess']
  
  def update_proximity_sensors(self):
    actions = [MOVE_RIGHT, MOVE_AHEAD, MOVE_LEFT, MOVE_BACK]
    directions = ['right', 'ahead', 'left', 'back']
    
    start_position = dict(self.last_event.metadata["agent"]["position"])
    distances = {}
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
      
