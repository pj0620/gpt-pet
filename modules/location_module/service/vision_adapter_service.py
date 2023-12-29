import os
from dataclasses import dataclass

import requests

@dataclass
class RoomDescription:
  description: str
  name: str

class VisionAdapterService:
  def __init__(self):
    self.vision_module_url = os.environ.get('VISION_MODULE_URL')
    print(f'found {self.vision_module_url=}')
    
  def describe_room(self, encoded_image: bytes) -> RoomDescription:
    data = {
      "image": encoded_image.decode('utf-8')
    }
    response = requests.post(f"{self.vision_module_url}/describe-room", json=data)
    if response.status_code == 200:
      print("successfully described room from image")
      json_desc = response.json()
      return RoomDescription(
        json_desc['description'],
        json_desc['name']
      )
    else:
      raise Exception(f"recieved {response.status_code} when calling {self.vision_module_url}/describe-room")