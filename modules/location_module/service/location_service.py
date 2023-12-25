import base64
import os
from urllib.parse import urlparse

import requests
import weaviate
# import psycopg2

from vectordb.constants import ROOM_CLASS_NAME, LOCATION_DB_SCHEMA_NAME
from vectordb.location_schema import LOCATION_VECTORDB_SCHEMA

class VisionService:
  def __init__(self):
    self.hardware_module_url = os.environ.get('HARDWARE_MODULE_URL')
    print(f'found {self.hardware_module_url=}')
    
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
    
    self.current_room = None
    
    self.setup_dbs(None)
  
  def setup_dbs(self, sql_module_url):
    # result = urlparse(sql_module_url)
    # username = result.username
    # password = result.password
    # database = result.path[1:]  # Remove leading slash
    # hostname = result.hostname
    # port = result.port
    #
    # # Connect to the database
    # self.sql_conn = psycopg2.connect(
    #   database=database,
    #   user=username,
    #   password=password,
    #   host=hostname,
    #   port=port
    # )
    
    print('checking if we need to recreate vector db')
    if os.environ.get('RECREATE_VECTOR_DB').lower() == 'true':
      print('recreating vector db')
      for class_config in LOCATION_VECTORDB_SCHEMA["classes"]:
        print(f"class_config = {class_config}")
        class_name = class_config["class"]
        print(f"checking if {class_name} exists")
        if self.vectordb_client.schema.exists(class_name):
          print(f'found class exists, deleting {class_name}')
          self.vectordb_client.schema.delete_class(class_name)
      
      print('creating db')
      self.vectordb_client.schema.create(LOCATION_VECTORDB_SCHEMA)
  
  def capture_room_view(self):
    print(f'getting capture of current view from {self.hardware_module_url}/capture-image')
    # Make a GET request to fetch the image
    response = requests.get(f'{self.hardware_module_url}/capture-image')
    
    # Check if the request was successful
    if response.status_code != 200:
      raise Exception(f"Cannot connect to self.environment_module_url at "
                      f"{self.hardware_module_url}/capture-image, "
                      f"recieved {response.status_code} response code")
    
    encoded_image = base64.b64encode(response.content).decode('utf-8')
    print(f"{encoded_image=}")
    
    if self.current_room is None:
      self.identify_current_room()
      
    
    
  def identify_current_room(self):
    # TODO: more logic
    return 0
