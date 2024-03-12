import os
from dataclasses import asdict

import weaviate

from constants.schema.vision_schema import PET_VIEW_CLASS_SCHEMA, PET_VIEW_CLASS_NAME, ROOM_VIEW_VECTORDB_SCHEMA
from constants.vectordb import VECTOR_DB_URL
from model.vision import CreatePetViewModel


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
    RECREATE_VECTOR_DB = os.environ.get('RECREATE_VECTOR_DB')
    if RECREATE_VECTOR_DB is not None and RECREATE_VECTOR_DB.lower() == 'true':
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
  
  def create_pet_view(self, new_pet_view: CreatePetViewModel):
    new_pet_view_id = self.vectordb_client.data_object.create(
      class_name=PET_VIEW_CLASS_NAME,
      data_object=asdict(new_pet_view)
    )
    print(f'successfully created new room with id: {new_pet_view_id}')
    return new_pet_view_id
  
  def delete_pet_view(self, pet_view_id: str):
    deleted_pet_view_id = self.vectordb_client.data_object.delete(
      class_name=PET_VIEW_CLASS_NAME,
      uuid=pet_view_id
    )
    print(f'successfully deleted new room with id: {deleted_pet_view_id}')
    return deleted_pet_view_id
  
  def get_similar_pet_views(self, image: str):
    sourceImage = {"image": image}
    
    raw_response = (self.vectordb_client.query.get(
      class_name=PET_VIEW_CLASS_NAME,
      properties=["description", "passageway_descriptions", "passageways"]
      ).with_near_image(
        sourceImage, encode=False
      ).with_additional(["distance", "id"])
      .with_limit(1).do())
    
    print(f'{raw_response=}')
    room_view_arr = raw_response['data']['Get']['RoomView']
    if len(room_view_arr) == 0:
      return []
    
    if room_view_arr[0]['_additional']['distance'] < 0.05:
      return room_view_arr
    else:
      return []