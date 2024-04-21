from typing import Any

import numpy as np
from pykinect2 import PyKinectRuntime

from gptpet_context import GPTPetContext
from module.sensory.base_sensory_module import BaseSensoryModule
from service.sim_adapter import SimAdapter


class PhysicalCameraModule(BaseSensoryModule):
  def __init__(
      self,
      kinect: PyKinectRuntime.PyKinectRuntime
  ):
    self.kinect = kinect
    self.last_frame = None
  
  def build_subconscious_input(self, context: GPTPetContext) -> dict[str, Any]:
    if self.kinect.has_new_color_frame():
      color_frame = self.kinect.get_last_color_frame()
      # color_frame = np.reshape(color_frame, (1080, 1920, 4))  # Change the shape into H x W x C
      # color_frame = color_frame[:, :, :3]  # Drop the alpha channel
      # frames['color'] = color_frame
      self.last_frame = color_frame
    print(f'{self.last_frame.shape=}')
    
    return {'last_frame': None}
