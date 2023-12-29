from datetime import datetime

from service.hardware_adapter_service import HardwareAdapterService
from service.vectordb_adapter_service import VectorDBAdapterService
from service.vision_adapter_service import VisionAdapterService

from model.location_models import Room


class LocationService:
  def __init__(self):
    self.hardware_adapter_service = HardwareAdapterService()
    self.vectordb_adapter_service = VectorDBAdapterService()
    self.vision_adapter_service = VisionAdapterService()
    
    self.current_room = None
  
  def capture_room_view(self):
    encoded_image = self.hardware_adapter_service.capture_image()
    
    if self.current_room is None:
      self.identify_current_room(encoded_image)
      
  def identify_current_room(self, encoded_image: str):
    # current room is set return current room
    # TODO: there is a chance current room is out of sync, add handling of this case
    if self.current_room is not None:
      print(f'returning current room from location module state: id={self.current_room}')
      return self.current_room
    
    # if room db is empty, no rooms are created. This is the first room we have ever seen. Create new room
    if self.vectordb_adapter_service.rooms_db_empty():
      self.create_new_room(encoded_image)
      print(f'created new room: {self.current_room}')
      return self.current_room
    
    # TODO: more logic
    return 0
  
  def create_new_room(self, encoded_image: str):
    room_description = self.vision_adapter_service.describe_room(encoded_image)
    print(room_description)
    
    current_time = datetime.utcnow().isoformat() + 'Z'
    new_room = Room(
      name=room_description.name,
      description=room_description.description,
      createdAt=current_time,
      modifiedAt=current_time,
      lastAccessedAt=current_time
    )
    self.current_room = self.vectordb_adapter_service.create_room(new_room)
