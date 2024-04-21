from typing import Any

import cv2
# this will fail in local avoid importing unless installed from source
import freenect
from gptpet_context import GPTPetContext
from module.sensory.base_sensory_module import BaseSensoryModule


class PhysicalCameraModule(BaseSensoryModule):
  
  def build_subconscious_input(self, context: GPTPetContext) -> dict[str, Any]:
    array, _ = freenect.sync_get_video()
    array = cv2.cvtColor(array, cv2.COLOR_RGB2BGR)
    return {'last_frame': array}
