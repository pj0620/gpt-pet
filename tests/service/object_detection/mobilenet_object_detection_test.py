import unittest

import cv2

from service.object_detection.mobilenet_object_detection import MobileNetObjectDetection


class MobileNetObjectDetectionTest(unittest.TestCase):
  def setUp(self):
    self.detect_service = MobileNetObjectDetection()
    
  def test_detect_objects(self):
    image = cv2.imread("room_view.png")
    image = cv2.resize(image, (640, 480))
    objects = self.detect_service.detect_objects(image)
    class_names = set(x.class_name for x in objects)
    expected_class_names = {'TV', 'CHAIR'}
    assert class_names == expected_class_names
    
