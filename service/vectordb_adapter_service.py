import os
from dataclasses import asdict

import weaviate

from constants.schema.vision_schema import PET_VIEW_CLASS_SCHEMA, PET_VIEW_CLASS_NAME, ROOM_VIEW_VECTORDB_SCHEMA
from constants.vectordb import VECTOR_DB_URL
from model.vision import PetView


class VectorDBAdapterService:
  def __init__(self):
    for try_count in range(10):
      print(f'trying to connect to weaviate attempt number: {try_count}')
      try:
        self.vectordb_client = weaviate.Client(
          VECTOR_DB_URL,
          timeout_config=(100, 60)
        )
        break
      except weaviate.exceptions.WeaviateStartUpError as e:
        print('failed to connect to weaviate', e)
    
    if self.vectordb_client is None:
      raise Exception("Could not connect to weaviate at " + VECTOR_DB_URL)
    
    self.setup_dbs()
  
  def setup_dbs(self):
    print('checking if we need to recreate vector db')
    if os.environ.get('RECREATE_VECTOR_DB').lower() == 'true':
      print('recreating vector db')
      for class_config in ROOM_VIEW_VECTORDB_SCHEMA["classes"]:
        class_name = class_config["class"]
        print(f"checking if {class_name} exists")
        if self.vectordb_client.schema.exists(class_name):
          print(f'found class exists, deleting {class_name}')
          self.vectordb_client.schema.delete_class(class_name)
      
      print('creating db')
      self.vectordb_client.schema.create(ROOM_VIEW_VECTORDB_SCHEMA)
  
  def get_pet_views(self,
                query_fields: list[str] = None):
    rooms = self.vectordb_client.query \
      .get(PET_VIEW_CLASS_SCHEMA, query_fields) \
      .do()
    return rooms['data']['Get']['description']
  
  def create_pet_view(self, new_pet_view: PetView):
    new_pet_view_id = self.vectordb_client.data_object.create(
      class_name=PET_VIEW_CLASS_NAME,
      data_object=asdict(new_pet_view)
    )
    print(f'successfully created new room with id: {new_pet_view_id}')
    return new_pet_view_id
  
  def get_similar_pet_views(self, image: str):
    sourceImage = {"image": image}
    
    raw_response = (self.vectordb_client.query.get(
      class_name=PET_VIEW_CLASS_NAME,
      properties=["description", "turn_percent"]
      ).with_near_image(
        sourceImage, encode=False
      ).with_additional(["distance"])
      .with_limit(1).do())
    
    room_view_arr = raw_response['data']['Get']['RoomView']
    if len(room_view_arr) == 0:
      return []
    
    if room_view_arr[0]['_additional']['distance'] < 0.1:
      return room_view_arr
    else:
      return []
  
  # def create_image(self, image_data: str | bytes):
  #   converted_img = image_data
  #   if isinstance(image_data, bytes):
  #     converted_img = image_data.decode('utf-8')
  #
  #   current_time = datetime.utcnow().isoformat() + 'Z'
  #   new_image = Image(
  #     image=converted_img,
  #     createdAt=current_time,
  #     modifiedAt=current_time,
  #     lastAccessedAt=current_time
  #   )
  #   new_image_id = self.vectordb_client.data_object.create(
  #     class_name=IMAGE_CLASS_NAME,
  #     data_object=asdict(new_image)
  #   )
  #   print(f'successfully created new image with id: {new_image_id}')
  #   return new_image_id
  #
  # def associate_room_with_image(self, room_id: str, image_id: str):
  #   self.vectordb_client.data_object.reference.add(
  #     from_class_name=ROOM_CLASS_NAME,
  #     from_uuid=room_id,
  #     from_property_name="images",
  #     to_class_name=IMAGE_CLASS_NAME,
  #     to_uuid=image_id,
  #   )