from typing import Any

import numpy as np

from constants.kinect import FREENECT_DEPTH_REGISTERED
from gptpet_context import GPTPetContext
from module.sensory.base_sensory_module import BaseSensoryModule
import cv2
# this will fail in local avoid importing unless installed from source
import freenect

from service.kinect.base_kinect_service import BaseKinectService


class AsyncPhysicalDepthCameraModule(BaseSensoryModule):
  def __init__(self, kinect_service: BaseKinectService):
    self.kinect_service = kinect_service
  
  def build_subconscious_input(self, context: GPTPetContext) -> dict[str, Any]:
    depth = self.kinect_service.get_depth()
    
    print(f"raw depth: shape={depth.shape}, min={depth.min()}, max={depth.max()}")
    
    depth = depth.astype('float64') / 1000.
    
    return {'last_depth_frame': depth}
