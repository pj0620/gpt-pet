from abc import ABC

from constants.motor import MOVE_RIGHT, MOVE_AHEAD, MOVE_LEFT, MOVE_BACK, ROTATE_RIGHT
from model.motor import MovementResult
from service.motor.base_motor_adapter import BaseMotorAdapter
from service.sensor.base_proximity_sensor_adapter import BaseProximitySensorAdapter
from tools.environment.api.base_control_api import BaseControlAPI


class ProdControlAPI(BaseControlAPI):
  motor_adapter: BaseMotorAdapter
  proximity_sensor_adapter: BaseProximitySensorAdapter
  
  def __init__(
      self,
      proximity_sensor_adapter: BaseProximitySensorAdapter,
      motor_adapter: BaseMotorAdapter
  ):
    self.proximity_sensor_adapter = proximity_sensor_adapter
    self.motor_adapter = motor_adapter
  
  def move_right(
      self,
      move_magnitude: float = None
  ) -> MovementResult:
    print(f"ProdControlAPI: executing move_right, {move_magnitude=}")
    return self.motor_adapter.do_movement(MOVE_RIGHT, move_magnitude=move_magnitude)
  
  def move_ahead(
      self,
      move_magnitude: float = None
  ) -> MovementResult:
    print(f"ProdControlAPI: executing move_ahead, {move_magnitude=}")
    return self.motor_adapter.do_movement(MOVE_AHEAD, move_magnitude=move_magnitude)
  
  def move_left(
      self,
      move_magnitude: float = None
  ) -> MovementResult:
    print(f"ProdControlAPI: executing move_left, {move_magnitude=}")
    return self.motor_adapter.do_movement(MOVE_LEFT, move_magnitude=move_magnitude)
  
  def move_back(
      self,
      move_magnitude: float = None
  ) -> MovementResult:
    print(f"ProdControlAPI: executing move_back, {move_magnitude=}")
    return self.motor_adapter.do_movement(MOVE_BACK, move_magnitude=move_magnitude)
  
  def rotate(
      self,
      degress: float = None
  ) -> MovementResult:
    print(f"ProdControlAPI: executing rotate, {degress=}")
    return self.motor_adapter.do_rotate(ROTATE_RIGHT, degrees=degress)