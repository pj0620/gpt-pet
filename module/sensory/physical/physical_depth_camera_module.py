from typing import Any

import numpy as np

from gptpet_context import GPTPetContext
from module.sensory.base_sensory_module import BaseSensoryModule
import cv2
# this will fail in local avoid importing unless installed from source
import freenect

# ref: https://stackoverflow.com/questions/12819599/freenect-depth-registered-has-no-effect-with-libfreenect
FREENECT_DEPTH_10BIT = 1
FREENECT_DEPTH_11BIT_PACKED = 2
FREENECT_DEPTH_10BIT_PACKED = 3
FREENECT_DEPTH_REGISTERED = 4
FREENECT_DEPTH_MM = 5
FREENECT_DEPTH_DUMMY = 2147483647

class PhysicalDepthCameraModule(BaseSensoryModule):
  
  def build_subconscious_input(self, context: GPTPetContext) -> dict[str, Any]:
    # Get depth data from the depth camera
    depth, _ = freenect.sync_get_depth(format=FREENECT_DEPTH_REGISTERED)
    
    print(f"raw depth: shape={depth.shape}, min={depth.min()}, max={depth.max()}")
    
    depth = depth.astype('float64') / 1000.
    
    return {'last_depth_frame': depth}
