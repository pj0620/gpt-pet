from typing import Any

import numpy as np

from constants.kinect import FREENECT_DEPTH_REGISTERED
from gptpet_context import GPTPetContext
from module.sensory.base_sensory_module import BaseSensoryModule
import cv2
# this will fail in local avoid importing unless installed from source
import freenect

class PhysicalDepthCameraModule(BaseSensoryModule):
  
  def build_subconscious_input(self, context: GPTPetContext) -> dict[str, Any]:
    # Get depth data from the depth camera
    depth, _ = freenect.sync_get_depth(format=FREENECT_DEPTH_REGISTERED)
    
    print(f"raw depth: shape={depth.shape}, min={depth.min()}, max={depth.max()}")
    
    depth = depth.astype('float64') / 1000.
    
    return {'last_depth_frame': depth}
