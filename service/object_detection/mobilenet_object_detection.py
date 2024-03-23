import os
from typing import Tuple

import cv2
import numpy as np

from model.objects import FoundObject
from service.object_detection.base_object_detection import BaseObjectDetection


class MobileNetObjectDetection(BaseObjectDetection):
  def __init__(self):
    base_data_dir = os.path.dirname(os.path.realpath(__file__))
    weights = f"{base_data_dir}/model/frozen_inference_graph.pb"
    model = f"{base_data_dir}/model/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
    self.net = cv2.dnn.readNetFromTensorflow(weights, model)
    
    self.class_names = []
    with open(f"{base_data_dir}/model/coco_names.txt", "r") as f:
      self.class_names = f.read().strip().split("\n")
    
  def detect_objects(self, image: np.array, output_image: np.array) -> tuple[np.array, list[FoundObject]]:
    h = image.shape[0]
    w = image.shape[1]
    
    blob = cv2.dnn.blobFromImage(
      image, 1.0 / 127.5, (320, 320), [127.5, 127.5, 127.5])
    # pass the blog through our network and get the output predictions
    self.net.setInput(blob)
    output = self.net.forward()
    
    objects = []
    for i, detection in enumerate(output[0, 0, :, :]):  # output[0, 0, :, :] has a shape of: (100, 7)
      # the confidence of the model regarding the detected object
      probability = detection[2]
      
      # if the confidence of the model is lower than 50%,
      # we do nothing (continue looping)
      if probability < 0.5:
        continue
      
      # perform element-wise multiplication to get
      # the (x, y) coordinates of the bounding box
      box = [int(a * b) for a, b in zip(detection[3:7], [w, h, w, h])]
      box = tuple(box)
      
      # extract the ID of the detected object to get its name
      class_id = int(detection[1])
      
      # draw the bounding box of the object
      cv2.rectangle(output_image, box[:2], box[2:], (0, 255, 0), thickness=2)
      label = f"Box {i}: {self.class_names[class_id - 1].upper()} {probability * 100:.2f}%"
      cv2.putText(output_image, label, (box[0], box[1] + 30),
                  cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
      
      objects.append(FoundObject(
        bbox=box,
        class_name=self.class_names[class_id - 1].upper(),
        probability=probability,
        index=i
      ))
  
    return output_image, objects
  