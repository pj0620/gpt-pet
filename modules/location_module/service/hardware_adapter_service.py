import os

import requests


class HardwareAdapterService:
  def __init__(self):
    self.hardware_module_url = os.environ.get('HARDWARE_MODULE_URL')
    print(f'found {self.hardware_module_url=}')
    
  def capture_image(self) -> bytes:
    print(f'getting capture of current view from {self.hardware_module_url}/capture-image')
    # Make a GET request to fetch the image
    response = requests.get(f'{self.hardware_module_url}/capture-image')
    
    # Check if the request was successful
    if response.status_code != 200:
      raise Exception(f"Cannot connect to self.environment_module_url at "
                      f"{self.hardware_module_url}/capture-image, "
                      f"recieved {response.status_code} response code")
    
    return response.content
    