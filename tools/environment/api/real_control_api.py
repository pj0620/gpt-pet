from constants.motor import MOVE_RIGHT, MOVE_AHEAD, MOVE_LEFT, MOVE_BACK, ROTATE_RIGHT, ROTATE_LEFT
from service.motor.base_motor_adapter import BaseMotorAdapter
from service.sensor.base_proximity_sensor_adapter import BaseProximitySensorAdapter
from tools.environment.api.base_control_api import BaseControlAPI


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
    return self.handle_action(ROTATE_LEFT, degrees)
  
  # No need to track proximity sensor actions for rollback procedure
  
  def read_back_sensor(
      self
  ) -> str:
    print(f"ProdControlAPI: executing read_back_sensor")
    return self.proximity_sensor_adapter.get_measurements()['back']
  
  def read_ahead_sensor(
      self
  ) -> str:
    print(f"ProdControlAPI: executing read_ahead_sensor")
    return self.proximity_sensor_adapter.get_measurements()['ahead']
  
  def read_left_sensor(
      self
  ) -> str:
    print(f"ProdControlAPI: executing read_left_sensor")
    return self.proximity_sensor_adapter.get_measurements()['left']
  
  def read_right_sensor(
      self
  ) -> str:
    print(f"ProdControlAPI: executing read_right_sensor")
    return self.proximity_sensor_adapter.get_measurements()['right']

  def handle_action(self, action: str, param: float):
    kwargs = {}
    if action == ROTATE_LEFT:
      kwargs = dict(degress=param)
      resp = self.motor_adapter.do_rotate(action, **kwargs)
    else:
      kwargs = dict(move_magnitude=param)
      resp = self.motor_adapter.do_movement(action, **kwargs)
    if resp.successful:
      self.push_new_action(action, params=kwargs)
      return "success!"
    else:
      raise Exception(f"failed with error: {action} while executing {action} with {kwargs}")