import time
from typing import Tuple

import numpy as np

from constants.motor import MOVE_RIGHT, MOVE_AHEAD, MOVE_LEFT, MOVE_BACK, ROTATE_RIGHT, ROTATE_LEFT
from gptpet_context import GPTPetContext
from model.collision import CollisionError, InvalidPassagewayError
from service.analytics_service import AnalyticsService
from service.device_io.base_device_io_adapter import BaseDeviceIOAdapter
from service.kinect.base_kinect_service import BaseKinectService
from service.motor.base_motor_service import BaseMotorService
from tools.environment.api.base_control_api import BaseControlAPI
import warnings

from utils.vision_utils import depth_arr_avg

PASSAGEWAY_STEP_DEGREES = 5
PASSAGEWAY_MAX_STEP_COUNT = 4
PASSAGEWAY_AVG_DEPTH_THRESHOLD = 0.5
PASSAGEWAY_STOP_TIME = 1


class RealControlAPI(BaseControlAPI):
  motor_adapter: BaseMotorService
  proximity_sensor_adapter: BaseDeviceIOAdapter
  
  def __init__(self,
               proximity_sensor_adapter: BaseDeviceIOAdapter,
               motor_adapter: BaseMotorService,
               context: GPTPetContext):
    super().__init__()
    self.proximity_sensor_adapter = proximity_sensor_adapter
    self.motor_adapter = motor_adapter
    self.kinect_service = context.kinect_service
    self.analytics_service = context.analytics_service
    self.context = context
  
  def tilt_up(self) -> None:
    self.context.kinect_service.do_tilt(30)
  
  def tilt_straight(self) -> None:
    self.context.kinect_service.do_tilt(-15)
  
  def tilt_down(self) -> None:
    self.context.kinect_service.do_tilt(-30)
  
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
      self, passageway_name: str
  ) -> str:
    passageway = self.get_passageway(passageway_name)
    degrees_to_turn = passageway.turn_degrees
    self.rotate(degrees_to_turn)
    turn_step_deg = PASSAGEWAY_STEP_DEGREES if degrees_to_turn > 0 else -PASSAGEWAY_STEP_DEGREES
    
    validated_depth, degrees_turned = self.turn_to_find_opening(degrees_to_turn, turn_step_deg)
    if not validated_depth:
      self.rotate(-degrees_turned)
      validated_depth, degrees_turned = self.turn_to_find_opening(0, -turn_step_deg)
      
      if not validated_depth:
        raise InvalidPassagewayError(f"passageway `{passageway_name}` is not traversable. Cannot move through "
                                     f"this passageway")
    
    time.sleep(0.5)
    dist = self.read_ahead_sensor() * 0.9
    
    if dist < 0.1:
      raise InvalidPassagewayError(f"passageway `{passageway_name}` is too close cannot move through it.")
    
    return self.move_ahead(dist)
  
  def turn_to_find_opening(self, initial_degrees: float, turn_step_deg: float) -> Tuple[bool, float]:
    total_degrees_turned = 0
    validated_depth = False
    for passageway_step in range(PASSAGEWAY_MAX_STEP_COUNT + 1):
      total_degrees_turned = initial_degrees + passageway_step * turn_step_deg
      avg_depth = depth_arr_avg(self.kinect_service.get_depth())
      self.analytics_service.new_text(f"checking depth sensor after turning {total_degrees_turned} degrees resulted "
                                      f"in avg_depth = {avg_depth}")
      if avg_depth >= PASSAGEWAY_AVG_DEPTH_THRESHOLD:
        validated_depth = True
        break
      
      self.analytics_service.new_text(f"{avg_depth} < {PASSAGEWAY_AVG_DEPTH_THRESHOLD}, rotating {turn_step_deg}")
      self.rotate(turn_step_deg)
      time.sleep(PASSAGEWAY_STOP_TIME)
    
    return validated_depth, total_degrees_turned
  
  def goto_object(self, object_name: str) -> str:
    print(f"RealControlAPI: going towards following object `{object_name}`")
    matching_objects = [p for p in self.objects if p.name.lower() == object_name.lower()]
    if len(matching_objects) == 0:
      raise Exception(f"failed to move toward object `{object_name}`. Does not exist. The only valid objects "
                      f"are {self.objects}")
    elif len(matching_objects) > 1:
      warnings.warn(f"found multiple objects with the same name {object_name} choosing first")
    found_object = matching_objects[0]
    degrees_to_turn = found_object.horizontal_angle
    self.rotate(degrees_to_turn)
    time.sleep(0.5)
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
