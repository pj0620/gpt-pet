from abc import ABC

import numpy as np


class BaseObjectDetection(ABC):
  def detect_objects(self, image: np.array):
    """
    :param image: numpy array representing image
    :return: objects in the image
    """
    pass