from abc import ABC, abstractmethod

import numpy as np

from model.objects import Object


class BaseObjectDetection(ABC):
  
  @abstractmethod
  def detect_objects(self, image: np.array, output_image: np.array) -> tuple[np.array, list[Object]]:
    """
    :param image: numpy array representing image
    :param output_image: image which object detection will label with bboxes
    :return: objects in the image
    """
    pass
