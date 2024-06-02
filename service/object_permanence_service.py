from dataclasses import dataclass

import numpy as np

from gptpet_context import GPTPetContext
from model.objects import Object, ObjectQueryModel, ObjectCreateModel, ObjectDescription
from service.vectordb_adapter_service import VectorDBAdapterService
from utils.serialization import serialize_dataclasses_dict


@dataclass
class LabelPassagewaysConfig:
  # used to control what part of the depth image should be average to compute a passageway
  top_clip_percent: float = 0.5
  bottom_clip_percent: float = 1
  
  # average distance to be considered a path forward
  passage_distance_threshold: float = 0.6
  
  # minimum width of a passage for robot to consider passing through it
  min_passage_width: int = 40
  
  # control where X labeling passages is placed vertically on the final image
  x_height_percent: float = 0.65


class ObjectPermanenceService:
  def __init__(
      self,
      vectordb_adapter_service: VectorDBAdapterService
  ):
    self.vectordb_adapter_service = vectordb_adapter_service
    self.config = LabelPassagewaysConfig()
  
  def augment_objects(
      self,
      context: GPTPetContext,
      objects_response: list[ObjectDescription],
      image_width: int,
      depth_frame: np.array
  ) -> list[Object]:
    create_objects: list[ObjectCreateModel] = []
    output_objects: list[Object] = []
    for object_desc in objects_response:
      image_height = depth_frame.shape[0]
      top_percent = self.config.top_clip_percent
      bottom_percent = self.config.bottom_clip_percent
      depth_image_arr_clipped = depth_frame[int(image_height * top_percent):int(image_height * bottom_percent), :]
      
      # compute average distances using depth camera view
      n_cols = depth_image_arr_clipped.shape[1]
      row_avgs = np.sum(depth_image_arr_clipped, axis=0) / n_cols
      
      # average in a band around object
      
      output_object = Object(
        # convert pixels to actual angle object is to gptpet
        horizontal_angle=(float(object_desc.horz_location) - image_width / 2) * (70 / image_width),
        object_distance=float(row_avgs[int(object_desc.horz_location)]),
        name=object_desc.name,
        description=object_desc.description,
        seen_before=False
      )
      
      similar_object = self.vectordb_adapter_service.get_similar_object(output_object.get_query_model())
      if similar_object is not None:
        output_object.seen_before = True
        
        # since this object already exists, use the name from memory
        output_object.name = similar_object.name
      
      create_objects.append(output_object.get_create_model())
      output_objects.append(output_object)
    
    context.analytics_service.new_text(f"objects: {output_objects}")
    
    self.vectordb_adapter_service.create_objects(create_objects)
    
    return output_objects
