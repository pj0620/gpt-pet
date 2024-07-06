from typing import Any

import cv2
# this will fail in local. avoid importing unless installed from source
import freenect
from gptpet_context import GPTPetContext
from module.sensory.base_sensory_module import BaseSensoryModule
from service.kinect.base_kinect_service import BaseKinectService


class AsyncPhysicalCameraModule(BaseSensoryModule):
  def __init__(self, kinect_service: BaseKinectService):
    self.kinect_service = kinect_service
  
  def build_subconscious_input(self, context: GPTPetContext) -> dict[str, Any]:
    return {'last_frame': self.kinect_service.get_video()}
