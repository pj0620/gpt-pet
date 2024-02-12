import cv2
import numpy as np
from ai2thor.controller import Controller

from constants.ai2thor import AI2THOR_CROUCH, AI2THOR_NOOP
from utils.math_utils import get_rotation_vector

WINDOW_NAME = 'Pet View'

cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

class SimAdapter:
  def __init__(self):
    self.controller = Controller(
      scene="FloorPlan2",
      gridSize=0.25,
      rotateStepDegrees=90,
      # camera properties
      # width=512,
      # height=512,
      width=1024,
      height=1024,
      fieldOfView=160
    )
    self.controller.step(AI2THOR_CROUCH)
    self.controller.step(
      action='AddThirdPartyCamera',
      rotation=dict(x=45, y=0, z=0),
      position=dict(x=0, y=0, z=0)
    )
    self.noop()
    
    self.last_event = None
  
  def noop(self):
    self.last_event = self.controller.step(AI2THOR_NOOP)
    self.update_camera()
    
  def update_camera(self):
    pos = self.last_event.metadata["agent"]["position"]
    rot = self.last_event.metadata["agent"]["rotation"]
    
    pos_arr = np.array([pos['x'], pos['y'], pos['z']])
    rot_arr = get_rotation_vector(**rot)
    
    # camera_offset = np.array([0, -0.75, 0])
    camera_offset = np.array([0, -0.7, 0])
    camera_pos_arr = pos_arr + 0.25 * rot_arr + camera_offset
    camera_pos = dict(
      x=camera_pos_arr[0],
      y=camera_pos_arr[1],
      z=camera_pos_arr[2]
    )
    
    # tilt camera
    rot_tilted = dict(
      x=rot['x'] - 25,
      y=rot['y'],
      z=rot['z']
    )
    
    self.controller.step(
      action="UpdateThirdPartyCamera",
      thirdPartyCameraId=0,
      position=camera_pos,
      rotation=rot_tilted,
      fieldOfView=90
    )
  
  def do_step(self, *args, **kwargs):
    self.last_event = self.controller.step(*args, **kwargs)
    self.update_camera()
  
  def get_view(self):
    if self.last_event is None:
      self.noop()
    # last_frame = self.last_event.third_party_camera_frames[0]
    last_frame = self.last_event.frame
    cv2.imshow(WINDOW_NAME, last_frame)
    cv2.waitKey(33)
    return last_frame
  
  def last_event_successful(self):
    if self.last_event is None:
      return False
    return self.last_event.metadata['lastActionSuccess']
