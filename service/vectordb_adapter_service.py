import os
from dataclasses import asdict
from typing import Any

import weaviate
from langchain_openai import OpenAIEmbeddings

from constants.schema.object_schema import OBJECT_VECTORDB_SCHEMA, OBJECT_CLASS_NAME
from constants.schema.skill_schema import SKILL_VECTORDB_SCHEMA, SKILL_CLASS_NAME
from constants.schema.task_schema import TASK_VECTORDB_SCHEMA
from constants.schema.vision_schema import PET_VIEW_CLASS_SCHEMA, PET_VIEW_CLASS_NAME, ROOM_VIEW_VECTORDB_SCHEMA
from constants.vectordb import OBJECT_SIMILARITY_THRESHOLD
from model.conscious import TaskDefinition, SavedTask
from model.objects import ObjectCreateModel, ObjectQueryModel, ObjectResponseModel
from model.skill_library import SkillCreateModel, FoundSkill
from model.vision import CreatePetViewModel
from service.analytics_service import AnalyticsService
from utils.env_utils import check_env_flag, get_env_var
from langchain_community.vectorstores import Weaviate
from requests.exceptions import ConnectionError


class VectorDBAdapterService:
  def __init__(self, analytics_service: AnalyticsService):
    self.analytics_service = analytics_service
    weaviate_vector_db_url = get_env_var("WEAVIATE_VECTOR_DB_URL")
    assert "OPENAI_API_KEY" in os.environ.keys(), "error: please set OPENAI_API_KEY, or switch embedding model"
    for try_count in range(10):
      print(f'trying to connect to weaviate attempt number: {try_count}')
      self.vectordb_client = None
      try:
        self.vectordb_client = weaviate.Client(
          weaviate_vector_db_url,
          timeout_config=(100, 60),
          additional_headers={
            "X-OpenAI-Api-Key": os.environ.get("OPENAI_API_KEY")
          }
        )
        break
      except (weaviate.exceptions.WeaviateStartUpError, ConnectionError) as e:
        print('failed to connect to weaviate', e)
    
    if self.vectordb_client is None:
      raise Exception("Could not connect to weaviate at " + weaviate_vector_db_url)
    
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
    
    self.cond_drop_schema('RECREATE_ROOM_VIEW_DB', ROOM_VIEW_VECTORDB_SCHEMA, 'room view')
    self.cond_drop_schema('RECREATE_SKILL_DB', SKILL_VECTORDB_SCHEMA, 'skill')
    self.cond_drop_schema('RECREATE_OBJECT_DB', OBJECT_VECTORDB_SCHEMA, 'object')
    self.cond_drop_schema('RECREATE_TASK_DB', TASK_VECTORDB_SCHEMA, 'task')
    
  def cond_drop_schema(self, env_var: str, schema: Any, schema_name: str) -> None:
    if check_env_flag(env_var):
      resp = input(f"(!!!) Are you sure you want to delete all {schema_name}s? (!!!) [Y/n]:")
      if resp == "Y":
        self.recreate_schema(schema)
  
  # Not safe commenting out until needed
  # def get_pet_views(self,
  #               query_fields: list[str] = None):
  #   rooms = self.vectordb_client.query \
  #     .get(PET_VIEW_CLASS_SCHEMA, query_fields) \
  #     .do()
  #   return rooms['data']['Get']['description']
  
  def create_pet_view(self, new_pet_view: CreatePetViewModel):
    try:
      new_pet_view_id = self.vectordb_client.data_object.create(
        class_name=PET_VIEW_CLASS_NAME,
        data_object=asdict(new_pet_view)
      )
    except ConnectionError as e:
      self.analytics_service.new_text("error: failed to create petview id from connection error")
      print(e)
      return None
      
    print(f'successfully created new room with id: {new_pet_view_id}')
    return new_pet_view_id
  
  def delete_pet_view(self, pet_view_id: str):
    try:
      deleted_pet_view_id = self.vectordb_client.data_object.delete(
        class_name=PET_VIEW_CLASS_NAME,
        uuid=pet_view_id
      )
    except ConnectionError as e:
      self.analytics_service.new_text("error: failed to delete petview id from connection error")
      print(e)
      return None
    
    print(f'successfully deleted new room with id: {deleted_pet_view_id}')
    return deleted_pet_view_id
  
  def get_similar_pet_views(self, image: str):
    sourceImage = {"image": image}
    
    try:
      raw_response = (self.vectordb_client.query.get(
        class_name=PET_VIEW_CLASS_NAME,
        properties=["description", "passageway_descriptions", "objects_descriptions", "passageways"]
        ).with_near_image(
          sourceImage, encode=False
        ).with_additional(["distance", "id"])
        .with_limit(1).do())
    except ConnectionError as e:
      self.analytics_service.new_text("error: failed to get_similar_pet_views from connection error")
      print(e)
      return []
    
    print(f'{raw_response=}')
    room_view_arr = raw_response['data']['Get']['RoomView']
    if len(room_view_arr) == 0:
      return []
    
    if room_view_arr[0]['_additional']['distance'] < 0.15:
      return room_view_arr
    else:
      return []
    
  def get_similar_skill(self, task_definition: TaskDefinition, skill_threshold: float) -> list[FoundSkill]:
    try:
      raw_response = self.weaviate_skill_lc.similarity_search_with_score(
        task_definition.task,
        k=4
      )
      print(f"found {len(raw_response)} skills that match the task `{task_definition.task}`")
    except ConnectionError as e:
      self.analytics_service.new_text("error: failed to get_similar_skill from connection error")
      print(e)
      return []
    
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
    try:
      new_skill_id = self.vectordb_client.data_object.create(
        class_name=SKILL_CLASS_NAME,
        data_object=asdict(new_skill)
      )
      print(f'successfully created new skill with id: {new_skill_id}')
    except ConnectionError as e:
      self.analytics_service.new_text("error: failed to create_skill from connection error")
      print(e)
      return None
    return new_skill_id
  
  def delete_skill(self, skill: FoundSkill):
    try:
      deleted_pet_view_id = self.vectordb_client.batch.delete_objects(
        class_name=SKILL_CLASS_NAME,
        where={
          'operator': 'Equal',
          'path': ['task'],
          'valueText': skill.task
        }
      )
    except ConnectionError as e:
      self.analytics_service.new_text("error: failed to delete_skill from connection error")
      print(e)
      return None
    print(f'successfully deleted skills with id: {deleted_pet_view_id}')
    return deleted_pet_view_id
  
  def create_objects(self, objects: list[ObjectCreateModel]):
    try:
      for object_inp in objects:
        self.vectordb_client.batch.add_data_object(
          class_name=OBJECT_CLASS_NAME,
          data_object=asdict(object_inp)
        )
      self.vectordb_client.batch.create_objects()
      print(f'successfully created new {len(objects)} objects')
    except ConnectionError as e:
      self.analytics_service.new_text("error: failed to create_objects from connection error")
      print(e)
  
  def create_task(self, task: SavedTask) -> str | None:
    try:
      new_task_id = self.vectordb_client.data_object.create(
        class_name=SKILL_CLASS_NAME,
        data_object=asdict(task)
      )
      print(f'successfully created new task with id: {new_task_id}')
    except ConnectionError as e:
      self.analytics_service.new_text("error: failed to create_task from connection error")
      print(e)
      return None
    return new_task_id
    
  def get_task(self, pet_view_id: str) -> SavedTask | None:
    self.analytics_service.new_text(f"error: searching for saved task for pet_view_id = {pet_view_id}")
    try:
      result = (
        self.vectordb_client.query
        .get("Task", ["task", "pet_view_id", "reasoning"])
        .with_where({
          "path": ["pet_view_id"],
          "operator": "Equal",
          "valueString": pet_view_id
        })
        .do()
      )
    except ConnectionError as e:
      self.analytics_service.new_text("error: failed to get_task from connection error")
      print(e)
      return None
    
    task_data = result['data']['Get']['Task']
    if task_data:
      self.analytics_service.new_text(f"found previous saved task: {task_data[0]}")
      task_data = task_data[0]  # Assuming only one result
      saved_task = SavedTask(task=task_data["task"], reasoning=task_data["reasoning"],
                             pet_view_id=task_data["pet_view_id"])
      return saved_task
    else:
      self.analytics_service.new_text("No task found with the given pet_view_id.")
  
  def get_similar_object(
      self,
      object: ObjectQueryModel
  ) -> ObjectResponseModel | None:
    try:
      raw_response = self.weaviate_object_lc.similarity_search_with_score(
        object.description,
        k=1
      )
    except ConnectionError as e:
      self.analytics_service.new_text("error: failed to get_similar_object from connection error")
      print(e)
      return
    
    if len(raw_response) == 0:
      return None
    
    raw_object = raw_response[0]
    self.analytics_service.new_text(f"found following object that matches the object most similarly `{object.name}` "
                                    f"with a score of {raw_object[1]} checking against threshold of "
                                    f"{OBJECT_SIMILARITY_THRESHOLD}")
    if raw_object[1] < OBJECT_SIMILARITY_THRESHOLD:
      return None
    
    return ObjectResponseModel(
      name=raw_object[0].metadata['object_name'],
      description=raw_object[0].page_content
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
