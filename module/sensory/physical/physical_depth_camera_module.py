from typing import Any

import numpy as np

from gptpet_context import GPTPetContext
from module.sensory.base_sensory_module import BaseSensoryModule
import cv2
# this will fail in local avoid importing unless installed from source
import freenect

class PhysicalDepthCameraModule(BaseSensoryModule):
  
  def build_subconscious_input(self, context: GPTPetContext) -> dict[str, Any]:
    # Get depth data from the depth camera
    depth, _ = freenect.sync_get_depth()
    
    depth /= 1000.
    
    return {'last_depth_frame': depth}
