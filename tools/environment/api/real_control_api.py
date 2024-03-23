from constants.motor import MOVE_RIGHT, MOVE_AHEAD, MOVE_LEFT, MOVE_BACK, ROTATE_RIGHT, ROTATE_LEFT
from service.motor.base_motor_adapter import BaseMotorAdapter
from service.sensor.base_proximity_sensor_adapter import BaseProximitySensorAdapter
from tools.environment.api.base_control_api import BaseControlAPI
import warnings

class RealControlAPI(BaseControlAPI):
  motor_adapter: BaseMotorAdapter
  proximity_sensor_adapter: BaseProximitySensorAdapter
  
  def __init__(self, proximity_sensor_adapter: BaseProximitySensorAdapter, motor_adapter: BaseMotorAdapter):
    super().__init__()
    self.proximity_sensor_adapter = proximity_sensor_adapter
    self.motor_adapter = motor_adapter
  
  def move_right(
      self,
      move_magnitude: float = None
  ) -> str:
    print(f"ProdControlAPI: executing move_right, {move_magnitude=}")
    return self.handle_action(MOVE_RIGHT, move_magnitude)
  
  def move_ahead(
      self,
      move_magnitude: float = None
  ) -> str:
    print(f"ProdControlAPI: executing move_ahead, {move_magnitude=}")
    return self.handle_action(MOVE_AHEAD, move_magnitude)
  
  def move_left(
      self,
      move_magnitude: float = None
  ) -> str:
    print(f"ProdControlAPI: executing move_left, {move_magnitude=}")
    return self.handle_action(MOVE_LEFT, move_magnitude)
  
  def move_back(
      self,
      move_magnitude: float = None
  ) -> str:
    print(f"ProdControlAPI: executing move_back, {move_magnitude=}")
    return self.handle_action(MOVE_BACK, move_magnitude)
  
  def rotate(
      self,
      degrees: float = None
  ) -> str:
    print(f"ProdControlAPI: executing rotate, {degrees=}")
    return self.handle_action(ROTATE_RIGHT, degrees)
  
  # No need to track proximity sensor actions for rollback procedure
  
  def read_back_sensor(
      self
  ) -> float:
    print(f"ProdControlAPI: executing read_back_sensor")
    return float(self.proximity_sensor_adapter.get_measurements()['back'])
  
  def read_ahead_sensor(
      self
  ) -> float:
    print(f"ProdControlAPI: executing read_ahead_sensor")
    return float(self.proximity_sensor_adapter.get_measurements()['ahead'])
  
  def read_left_sensor(
      self
  ) -> float:
    print(f"ProdControlAPI: executing read_left_sensor")
    return float(self.proximity_sensor_adapter.get_measurements()['left'])
  
  def read_right_sensor(
      self
  ) -> float:
    print(f"ProdControlAPI: executing read_right_sensor")
    return float(self.proximity_sensor_adapter.get_measurements()['right'])
  
  def goto_passageway(
      self, passageway_color: str
  ) -> str:
    print(f"RealControlAPI: going down '{passageway_color}' passageway")
    matching_passageways = [p for p in self.passageways if p.color == passageway_color]
    if len(matching_passageways) == 0:
      raise Exception(f"failed to move down {passageway_color} passageway. Does not exist. The only valid passageways "
                      f"are {self.passageways}")
    elif len(matching_passageways) > 1:
      warnings.warn(f"found multiple passageways with the same color {passageway_color} choosing first")
    passageway = matching_passageways[0]
    degrees_to_turn = passageway.turn_degrees
    self.rotate(degrees_to_turn)
    dist = min(self.read_ahead_sensor() * 0.9, 10)
    return self.move_ahead(dist)
  
  def goto_object(self, object_name: str) -> str:
    print(f"RealControlAPI: going towards following object `{object_name}`")
    matching_objects = [p for p in self.objects if p.name == object_name]
    if len(matching_objects) == 0:
      raise Exception(f"failed to move toward object `{object_name}`. Does not exist. The only valid objects "
                      f"are {self.objects}")
    elif len(matching_objects) > 1:
      warnings.warn(f"found multiple objects with the same name {object_name} choosing first")
    found_object = matching_objects[0]
    degrees_to_turn = found_object.horizontal_angle
    self.rotate(degrees_to_turn)
    dist = min(self.read_ahead_sensor() * 0.9, 10)
    return self.move_ahead(dist)

  def handle_action(self, action: str, param: float):
    if 'Rotate' in action:
      kwargs = dict(degrees=param)
      resp = self.motor_adapter.do_rotate(action, **kwargs)
    else:
      kwargs = dict(move_magnitude=param)
      resp = self.motor_adapter.do_movement(action, **kwargs)
    if resp.successful:
      self.push_new_action(action, params=kwargs)
      return "success!"
    else:
      raise Exception(f"failed with error: {action} while executing {action} with {kwargs}")