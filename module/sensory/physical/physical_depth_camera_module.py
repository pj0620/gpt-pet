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
    
    # Depth data returned by freenect is a numpy array of unsigned 16-bit integers (uint16)
    # where each value represents the depth in millimeters.
    
    # Convert depth to a visual format (normalized 0-255 scale for display purposes)
    # Normalizing from assumed reasonable depth range (0mm to 2048mm)
    print("max: ", depth.max())
    print("min: ", depth.min())
    normalized_depth = (depth / 2048 * 255).astype(np.uint8)
    
    # Optionally apply a colormap for better visualization
    # COLORMAP_JET is commonly used for depth visualization
    depth_colored = cv2.applyColorMap(normalized_depth, cv2.COLORMAP_JET)
    
    return {'last_depth_frame': depth_colored}
