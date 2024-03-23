import os
from dataclasses import asdict
from typing import SupportsIndex, Any

import weaviate
from langchain_openai import OpenAIEmbeddings

from constants.schema.object_schema import OBJECT_VECTORDB_SCHEMA, OBJECT_CLASS_NAME
from constants.schema.skill_schema import SKILL_VECTORDB_SCHEMA, SKILL_CLASS_NAME, SKILL_DB_SCHEMA_NAME
from constants.schema.vision_schema import PET_VIEW_CLASS_SCHEMA, PET_VIEW_CLASS_NAME, ROOM_VIEW_VECTORDB_SCHEMA, \
  PET_VIEW_DB_SCHEMA_NAME
from constants.vectordb import VECTOR_DB_URL, OBJECT_SIMILARITY_THRESHOLD
from model.conscious import TaskDefinition
from model.objects import ObjectCreateModel, ObjectQueryModel, ObjectResponseModel
from model.skill_library import SkillCreateModel, FoundSkill
from model.vision import CreatePetViewModel
from utils.env_utils import check_env_flag
from langchain_community.vectorstores import Weaviate


class VectorDBAdapterService:
  def __init__(self):
    assert "OPENAI_API_KEY" in os.environ.keys(), "error: please set OPENAI_API_KEY, or switch embedding model"
    for try_count in range(10):
      print(f'trying to connect to weaviate attempt number: {try_count}')
      try:
        self.vectordb_client = weaviate.Client(
          VECTOR_DB_URL,
          timeout_config=(100, 60),
          additional_headers={
            "X-OpenAI-Api-Key": os.environ.get("OPENAI_API_KEY")
          }
        )
        break
      except weaviate.exceptions.WeaviateStartUpError as e:
        print('failed to connect to weaviate', e)
    
    if self.vectordb_client is None:
      raise Exception("Could not connect to weaviate at " + VECTOR_DB_URL)
    
    self.setup_dbs()
    
    self.weaviate_skill_lc = Weaviate(
      self.vectordb_client,
      index_name=SKILL_CLASS_NAME,
      text_key="task",
      embedding=OpenAIEmbeddings(),
      attributes=["code"]
    )
    self.weaviate_object_lc = Weaviate(
      self.vectordb_client,
      index_name=OBJECT_CLASS_NAME,
      text_key="object_description",
      embedding=OpenAIEmbeddings(),
      attributes=["object_name"]
    )
  
  def setup_dbs(self):
    print('checking if we need to recreate vector db')
    if check_env_flag('RECREATE_ROOM_VIEW_DB'): self.recreate_schema(ROOM_VIEW_VECTORDB_SCHEMA)
    if check_env_flag('RECREATE_SKILL_DB'): self.recreate_schema(SKILL_VECTORDB_SCHEMA)
    if check_env_flag('RECREATE_OBJECT_DB'): self.recreate_schema(OBJECT_VECTORDB_SCHEMA)
  
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
      properties=["description", "passageway_descriptions", "objects_descriptions", "passageways"]
      ).with_near_image(
        sourceImage, encode=False
      ).with_additional(["distance", "id"])
      .with_limit(1).do())
    
    print(f'{raw_response=}')
    room_view_arr = raw_response['data']['Get']['RoomView']
    if len(room_view_arr) == 0:
      return []
    
    if room_view_arr[0]['_additional']['distance'] < 0.01:
      return room_view_arr
    else:
      return []
    
  def get_similar_skill(self, task_definition: TaskDefinition, skill_threshold: float) -> list[FoundSkill]:
    raw_response = self.weaviate_skill_lc.similarity_search_with_score(
      task_definition.task,
      k=4
    )
    print(f"found {len(raw_response)} skills that match the task `{task_definition.task}`")
    
    return [
      FoundSkill(
        code=doc[0].metadata['code'],
        task=doc[0].page_content,
        score=doc[1]
      )
      for doc in raw_response
      if doc[1] >= skill_threshold
    ]
  
  def create_skill(self, new_skill: SkillCreateModel):
    new_skill_id = self.vectordb_client.data_object.create(
      class_name=SKILL_CLASS_NAME,
      data_object=asdict(new_skill)
    )
    print(f'successfully created new skill with id: {new_skill_id}')
    return new_skill_id
  
  def delete_skill(self, skill: FoundSkill):
    deleted_pet_view_id = self.vectordb_client.batch.delete_objects(
      class_name=SKILL_CLASS_NAME,
      where={
        'operator': 'Equal',
        'path': ['task'],
        'valueText': skill.task
      }
    )
    print(f'successfully deleted skills with id: {deleted_pet_view_id}')
    return deleted_pet_view_id
  
  def create_objects(self, objects: list[ObjectCreateModel]):
    for object_inp in objects:
      self.vectordb_client.batch.add_data_object(
        class_name=OBJECT_CLASS_NAME,
        data_object=asdict(object_inp)
      )
    self.vectordb_client.batch.create_objects()
    print(f'successfully created new {len(objects)} objects')
  
  def get_similar_object(
      self,
      object: ObjectQueryModel
  ) -> ObjectResponseModel | None:
    raw_response = self.weaviate_object_lc.similarity_search_with_score(
      object.description,
      k=1
    )
    print(f"found {len(raw_response)} objects that match the object `{object.name}`")
    
    if len(raw_response) == 0:
      return None
    
    raw_object = raw_response[0]
    if raw_object[1] < OBJECT_SIMILARITY_THRESHOLD:
      return None
    
    print(f"raw_object: {raw_object}")
    
    return ObjectResponseModel(
      name = raw_object[0].metadata['object_name'],
      description = raw_object[0].page_content
    )
  
  def recreate_schema(self, schema: Any) -> None:
    print(f'deleting recreating {schema["name"]} schema')
    for class_config in schema["classes"]:
      class_name = class_config["class"]
      print(f"checking if {class_name} exists")
      if self.vectordb_client.schema.exists(class_name):
        print(f'found class exists, deleting {class_name}')
        self.vectordb_client.schema.delete_class(class_name)
    self.vectordb_client.schema.create(schema)
