import cv2
import numpy as np
from ai2thor.controller import Controller

from constants.ai2thor import AI2THOR_CROUCH, AI2THOR_NOOP
from utils.math_utils import get_rotation_vector, dict_to_array

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
      # fieldOfView=90
    )
    self.controller.step(AI2THOR_CROUCH)
    self.controller.step(
      action='AddThirdPartyCamera',
      rotation=dict(x=0, y=0, z=0),
      position=dict(x=0, y=1, z=0),
      fieldOfView=90
    )
    self.noop()
  
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
  
  def do_step(self, *args, **kwargs):
    self.last_event = self.controller.step(*args, **kwargs)
    self.update_camera()
    self.update_proximity_sensors()
  
  def get_view(self):
    self.noop()
    third_party_last_frame = self.last_event.third_party_camera_frames[0]
    last_frame = self.last_event.frame
    cv2.imshow(WINDOW_NAME, third_party_last_frame)
    cv2.waitKey(33)
    return last_frame
  
  def last_event_successful(self):
    if self.last_event is None:
      return False
    return self.last_event.metadata['lastActionSuccess']
  
  def update_proximity_sensors(self):
    direction = 'x'
    dir_idx = {
      'x': 0,
      'y': 1,
      'z': 2,
    }[direction]
    pos = dict_to_array(self.last_event.metadata["agent"]["position"])
    rot = dict_to_array(self.last_event.metadata["agent"]["rotation"])
    
    min_ortho = float('inf')
    rect_bl = np.array([float('-inf'), float('-inf'), float('-inf')])
    rect_tr = np.array([float('inf'), float('inf'), float('inf')])
    for object_info in self.last_event.metadata["objects"]:
      axis_aligned_bounding_box = object_info["axisAlignedBoundingBox"]
      
      min_ortho_corner = float('inf')
      rect_bl_c = np.array([float('-inf'), float('-inf'), float('-inf')])
      rect_tr_c = np.array([float('inf'), float('inf'), float('inf')])
      for corner in axis_aligned_bounding_box["cornerPoints"]:
        min_ortho_corner = min(
          min_ortho_corner,
          corner[dir_idx]
        )
        rect_bl_c = np.minimum(
          rect_bl_c,
          np.array(corner)
        )
        rect_tr_c = np.maximum(
          rect_tr_c,
          np.array(corner)
        )
      
      if min_ortho_corner > pos[dir_idx]:
        min_ortho = min(min_ortho, min_ortho_corner)
    
    print('min_ortho: ', min_ortho, ', pos[dir_idx]:', pos[dir_idx])
      
      
