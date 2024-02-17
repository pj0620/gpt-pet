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
      scene="FloorPlan1",
      gridSize=0.25,
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
    print()
    self.update_camera()
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
    direction = 'z'
    dir_idx = {
      'x': 0,
      'y': 1,
      'z': 2,
    }[direction]
    pos = dict_to_array(self.last_event.metadata["agent"]["position"])
    # pos[1] = 0.25
    # rot = dict_to_array(self.last_event.metadata["agent"]["rotation"])
    rot = np.array([0., 0., 1.])
    
    min_ortho = float('inf')
    max_ortho = float('-inf')
    for object_info in self.last_event.metadata["objects"]:
      if not object_info["visible"]:
        continue
      
      print('#' * 40)
      print(f'{object_info['name']=}')
      
      print(f'pos: {pos}')
      print(f'rot: {rot}')
      
      axis_aligned_bounding_box = object_info["axisAlignedBoundingBox"]
      
      # find bottom right, and top left corners of this bounding rect
      bottom_left_corner = np.array([float('inf'), float('inf'), float('inf')])
      top_right_corner = np.array([float('-inf'), float('-inf'), float('-inf')])
      for corner in axis_aligned_bounding_box["cornerPoints"]:
        print(f'corner: {np.array(corner)}')
        bottom_left_corner = np.minimum(
          bottom_left_corner,
          np.array(corner)
        )
        top_right_corner = np.maximum(
          top_right_corner,
          np.array(corner)
        )
      
      print(f"bottom_left_corner: {bottom_left_corner}, top_right_corner: {top_right_corner}")
      
      # find distance from sensor to surface of box aligned
      aligned_diff_bl = bottom_left_corner[dir_idx] - pos[dir_idx]
      aligned_diff_tr = top_right_corner[dir_idx] - pos[dir_idx]
      aligned_diff = aligned_diff_bl
      if abs(aligned_diff_tr) < abs(aligned_diff_bl):
        aligned_diff = aligned_diff_tr
        
      print(f'{aligned_diff=}')
      
      # find point from sensor that may lie inside surface
      print(f"{rot=}, {pos=}")
      point_toward_plane = (aligned_diff / rot[dir_idx]) * rot + pos
      print(f"{point_toward_plane=}")
      
      # project to plane normal to sensor
      proj_idxes = [i for i in range(3) if i != dir_idx]
      bl_proj = bottom_left_corner[proj_idxes]
      tr_proj = top_right_corner[proj_idxes]
      pos_proj = point_toward_plane[proj_idxes]
      print(f"{bl_proj=}, {tr_proj=}, {pos_proj=}")
      
      in_surface = True
      for idx in range(2):
        in_surface = in_surface and (bl_proj[idx] <= pos_proj[idx] <= tr_proj[idx])
      print(f"{in_surface=}")
      
      if in_surface:
        min_ortho = min(min_ortho, aligned_diff)
        max_ortho = max(max_ortho, aligned_diff)
        print(f'updated: {min_ortho=}, {max_ortho=}')
    
    print(f'{min_ortho=}, {max_ortho=}')
      
      
