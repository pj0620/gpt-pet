from gptpet_context import GPTPetContext
from model.objects import Object, ObjectQueryModel, ObjectCreateModel
from service.vectordb_adapter_service import VectorDBAdapterService
from utils.serialization import serialize_dataclasses_dict


class ObjectPermanenceService:
  def __init__(
      self,
      vectordb_adapter_service: VectorDBAdapterService
  ):
    self.vectordb_adapter_service = vectordb_adapter_service
    
  def augment_objects(
      self,
      context: GPTPetContext,
      raw_objects_response: list[dict[str, str]],
      image_width: int
  ) -> list[Object]:
    create_objects: list[ObjectCreateModel] = []
    output_objects: list[Object] = []
    for obj_dict in raw_objects_response:
      if ("name" not in obj_dict) or ("description" not in obj_dict) or ("horz_location" not in obj_dict):
        continue
      
      output_object = Object(
        # convert pixels to actual angle object is to gptpet
        horizontal_angle=(float(obj_dict["horz_location"]) - image_width / 2) * (70 / image_width),
        name=obj_dict["name"],
        description=obj_dict["description"],
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
