import os
from dataclasses import asdict
from datetime import datetime

import weaviate

from model.location_models import Room, Image
from vectordb.constants import ROOM_CLASS_NAME, IMAGE_CLASS_NAME
from vectordb.location_schema import LOCATION_VECTORDB_SCHEMA


class VectorDBAdapterService:
  def __init__(self):
    vector_db_url = os.environ.get('VECTOR_DB_MODULE_URL')
    print(f'found {vector_db_url=}')
    for try_count in range(10):
      print(f'trying to connect to weaviate attempt number: {try_count}')
      try:
        self.vectordb_client = weaviate.Client(
          vector_db_url,
          timeout_config=(100, 60)
        )
        break
      except weaviate.exceptions.WeaviateStartUpError as e:
        print('failed to connect to weaviate', e)
    
    if self.vectordb_client is None:
      raise Exception("Could not connect to weaviate at " + vector_db_url)
    
    self.setup_dbs()
  
  def setup_dbs(self):
    print('checking if we need to recreate vector db')
    if os.environ.get('RECREATE_VECTOR_DB').lower() == 'true':
      print('recreating vector db')
      for class_config in LOCATION_VECTORDB_SCHEMA["classes"]:
        class_name = class_config["class"]
        print(f"checking if {class_name} exists")
        if self.vectordb_client.schema.exists(class_name):
          print(f'found class exists, deleting {class_name}')
          self.vectordb_client.schema.delete_class(class_name)
      
      print('creating db')
      self.vectordb_client.schema.create(LOCATION_VECTORDB_SCHEMA)
      
  def get_rooms(self,
                query_fields: list[str] = None):
    rooms = self.vectordb_client.query\
      .get(ROOM_CLASS_NAME,query_fields)\
      .do()
    return rooms['data']['Get']['Room']
  
  def rooms_db_empty(self):
    rooms_resp = self.vectordb_client.query \
      .get(ROOM_CLASS_NAME, ["name"])\
      .with_limit(1)\
      .do()
    rooms_lst: list[str] = rooms_resp['data']['Get']['Room']
    
    return len(rooms_lst) == 0
  
  def create_room(self, new_room: Room):
    new_room_id = self.vectordb_client.data_object.create(
      class_name=ROOM_CLASS_NAME,
      data_object=asdict(new_room)
    )
    print(f'successfully created new room with id: {new_room_id}')
    return new_room_id
  
  def create_image(self, image_data: str | bytes):
    converted_img = image_data
    if isinstance(image_data, bytes):
      converted_img = image_data.decode('utf-8')
    
    current_time = datetime.utcnow().isoformat() + 'Z'
    new_image = Image(
      image=converted_img,
      createdAt=current_time,
      modifiedAt=current_time,
      lastAccessedAt=current_time
    )
    new_image_id = self.vectordb_client.data_object.create(
      class_name=IMAGE_CLASS_NAME,
      data_object=asdict(new_image)
    )
    print(f'successfully created new room with id: {new_image_id}')
    return new_image_id
  
  def associate_room_with_image(self, room_id: str, image_id: str):
    self.vectordb_client.data_object.reference.add(
      from_class_name=ROOM_CLASS_NAME,
      from_uuid=room_id,
      from_property_name="images",
      to_class_name=IMAGE_CLASS_NAME,
      to_uuid=image_id,
    )