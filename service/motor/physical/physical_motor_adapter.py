import itertools
import json
from time import sleep
from typing import Literal

import RPi.GPIO as GPIO
import numpy as np

from constants.gpio.gpio_constants import FORWARD, FACES, SIDES, BACK, DIRECTIONS, BACKWARD, FRONT, LEFT, RIGHT, \
  MOTOR_CONTROLLERS
from constants.kinect import FREENECT_DEPTH_REGISTERED
from constants.motor import LINEAR_ACTIONS, MOVE_AHEAD, MOVE_BACK, MOVE_LEFT, MOVE_RIGHT, ROTATE_ACTIONS, ROTATE_RIGHT, \
  ROTATE_LEFT, MIN_WALL_DIST
from constants.physical_motor import *
from gptpet_context import GPTPetContext
from model.collision import CollisionError, StuckError
from model.motor import MovementResult
from service.device_io.base_device_io_adapter import BaseDeviceIOAdapter
from service.motor.base_motor_adapter import BaseMotorAdapter

import freenect

GPIO.setmode(GPIO.BOARD)
with open('constants/gpio/gpio.json', 'r') as file:
  gpio = json.load(file)


class PhysicalMotorService(BaseMotorAdapter):
  def __init__(
      self,
      context: GPTPetContext
  ):
    with open('constants/gpio/gpio.json', 'r') as file:
      self.gpio = json.load(file)
    self.context = context
  
  def do_movement(
      self,
      action: str,
      move_magnitude: float = 1
  ) -> MovementResult:
    assert action in LINEAR_ACTIONS, f'invalid movement action {action}'
    
    direction = ACTION_TO_DIRECTION[action]
    dist = float(self.context.device_io_adapter.get_measurements()[direction])
    if dist < MIN_WALL_DIST:
      error_msg = (f"Action '{action}' aborted: moveMagnitude {move_magnitude} exceeds proximity in {direction} "
                   f"({dist}m < minimum {MIN_WALL_DIST}m)")
      self.context.analytics_service.new_text(error_msg)
      raise CollisionError(error_msg)
    
    move_magnitude = min(move_magnitude, 1.)
    
    duty_cycle_width = HORZ_DUTY_CYCLE_WIDTH
    cycle_on = HORZ_CYCLE_ON
    duration = HORZ_ONE_METER_DURATION * move_magnitude
    if action == MOVE_AHEAD:
      duty_cycle_width = VERT_DUTY_CYCLE_WIDTH
      cycle_on = VERT_CYCLE_ON
      duration = VERT_ONE_METER_DURATION * move_magnitude
      on_pins = [
        self.gpio[face][side][FORWARD]
        for face, side in itertools.product(FACES, SIDES)
      ]
      off_pins = [
        self.gpio[face][side][BACKWARD]
        for face, side in itertools.product(FACES, SIDES)
      ]
    elif action == MOVE_BACK:
      duty_cycle_width = VERT_DUTY_CYCLE_WIDTH
      cycle_on = VERT_CYCLE_ON
      duration = VERT_ONE_METER_DURATION * move_magnitude
      on_pins = [
        self.gpio[face][side][BACKWARD]
        for face, side in itertools.product(FACES, SIDES)
      ]
      off_pins = [
        self.gpio[face][side][FORWARD]
        for face, side in itertools.product(FACES, SIDES)
      ]
    elif action == MOVE_LEFT:
      on_pins = [
        self.gpio[FRONT][LEFT][BACKWARD],
        self.gpio[BACK][RIGHT][BACKWARD],
        self.gpio[BACK][LEFT][FORWARD],
        self.gpio[FRONT][RIGHT][FORWARD]
      ]
      off_pins = [
        self.gpio[FRONT][LEFT][FORWARD],
        self.gpio[BACK][RIGHT][FORWARD],
        self.gpio[BACK][LEFT][BACKWARD],
        self.gpio[FRONT][RIGHT][BACKWARD]
      ]
    elif action == MOVE_RIGHT:
      on_pins = [
        self.gpio[FRONT][LEFT][FORWARD],
        self.gpio[BACK][RIGHT][FORWARD],
        self.gpio[BACK][LEFT][BACKWARD],
        self.gpio[FRONT][RIGHT][BACKWARD]
      ]
      off_pins = [
        self.gpio[FRONT][LEFT][BACKWARD],
        self.gpio[BACK][RIGHT][BACKWARD],
        self.gpio[BACK][LEFT][FORWARD],
        self.gpio[FRONT][RIGHT][FORWARD]
      ]
    else:
      raise Exception('Not implemented')
    
    self._do_action(
      on_pins=on_pins,
      off_pins=off_pins,
      duty_cycle_width=duty_cycle_width,
      cycle_on=cycle_on,
      duration=duration,
      direction=direction
    )
    
    return MovementResult(
      successful=True,
      action=action,
    )
  
  def stop(self):
    all_pins = [
      self.gpio[face][side][direction]
      for face, side, direction in itertools.product(FACES, SIDES, DIRECTIONS)
    ]
    
    GPIO.setmode(GPIO.BOARD)
    
    for p in all_pins:
      GPIO.setup(p, GPIO.OUT, initial=GPIO.LOW)
    
    sleep(1)
    
    for p in all_pins:
      GPIO.output(p, GPIO.LOW)
    
    GPIO.cleanup()
  
  def setup_motors(self):
    motor_control_pins = self.gpio[MOTOR_CONTROLLERS]
    
    GPIO.setmode(GPIO.BOARD)
    
    for p in motor_control_pins:
      GPIO.setup(p, GPIO.OUT, initial=GPIO.LOW)
      GPIO.output(p, GPIO.LOW)
    
    GPIO.cleanup()
  
  def do_rotate(
      self,
      action: str,
      degrees: float = None
  ) -> MovementResult:
    assert action in ROTATE_ACTIONS, f'invalid rotate action {action}'
    
    if abs(degrees) > 45:
      degrees = min(45., degrees)
      degrees = max(-45., degrees)
    
    fixed_action = action
    fixed_degrees = degrees
    if degrees < 0:
      fixed_action = INVERSE_ROTATE_ACTIONS[action]
      fixed_degrees *= -1
    
    if fixed_action == ROTATE_RIGHT:
      on_pins = [
        self.gpio[FRONT][LEFT][FORWARD],
        self.gpio[FRONT][RIGHT][BACKWARD],
        self.gpio[BACK][LEFT][FORWARD],
        self.gpio[BACK][RIGHT][BACKWARD]
      ]
      off_pins = [
        self.gpio[FRONT][LEFT][BACKWARD],
        self.gpio[FRONT][RIGHT][FORWARD],
        self.gpio[BACK][LEFT][BACKWARD],
        self.gpio[BACK][RIGHT][FORWARD]
      ]
    elif fixed_action == ROTATE_LEFT:
      off_pins = [
        self.gpio[FRONT][LEFT][FORWARD],
        self.gpio[FRONT][RIGHT][BACKWARD],
        self.gpio[BACK][LEFT][FORWARD],
        self.gpio[BACK][RIGHT][BACKWARD]
      ]
      on_pins = [
        self.gpio[FRONT][LEFT][BACKWARD],
        self.gpio[FRONT][RIGHT][FORWARD],
        self.gpio[BACK][LEFT][BACKWARD],
        self.gpio[BACK][RIGHT][FORWARD]
      ]
    else:
      raise Exception("action not implemented " + action)
    
    duration = (fixed_degrees / 360.) * FULL_TURN_DURATION
    print("spinning for a duration of ", duration)
    self._do_action(
      on_pins=on_pins,
      off_pins=off_pins,
      duty_cycle_width=ROT_DUTY_CYCLE_WIDTH,
      cycle_on=ROT_CYCLE_ON,
      duration=duration,
      direction=None,
      stop_after=False
    )
    
    return MovementResult(
      successful=True,
      action=action,
      degrees=degrees
    )
  
  def _do_action(
      self,
      on_pins: list[int],
      off_pins: list[int],
      duty_cycle_width: int,
      cycle_on: int,
      duration: float,
      direction: Literal['right', 'ahead', 'left', 'back'] | None,
      stop_after: bool = True
  ):
    print("calculating before average depth")
    before_avg_depth = self._calc_average_dist()
    
    GPIO.setmode(GPIO.BOARD)
    
    for p in off_pins:
      GPIO.setup(p, GPIO.OUT, initial=GPIO.LOW)
    for p in on_pins:
      GPIO.setup(p, GPIO.OUT, initial=GPIO.LOW)
    
    last_value = GPIO.LOW
    for division in range(int(duration * TIME_DIVISIONS_PER_SECOND)):
      new_value = GPIO.LOW
      if division % duty_cycle_width < cycle_on:
        new_value = GPIO.HIGH
      if last_value != new_value:
        for p in on_pins:
          GPIO.output(p, new_value)
        last_value = new_value
      
      sleep(TIME_DIVISION_STEP)
    
    for p in on_pins:
      GPIO.output(p, GPIO.LOW)
    
    # go backwards momentarily to stop robot
    if stop_after:
      for p in off_pins:
        GPIO.output(p, GPIO.HIGH)
      stop_time = min(0.05, duration * 0.25)
      sleep(stop_time)
    for p in [*off_pins, *on_pins]:
      GPIO.output(p, GPIO.LOW)
    
    GPIO.cleanup()
    
    print("calculating after average depth")
    after_avg_depth = self._calc_average_dist()
    
    perc_change_depth = abs((after_avg_depth - before_avg_depth) / before_avg_depth)
    if perc_change_depth < 0.05:
      error_msg = f"Action failed: depth sensor measurement indicate that movement failed."
      self.context.analytics_service.new_text(error_msg + f"; before: {before_avg_depth}, after: {after_avg_depth}")
      raise StuckError(error_msg)
  
  def _calc_average_dist(self):
    print("calculating average depth from depth sensor")
    
    depth, _ = freenect.sync_get_depth(format=FREENECT_DEPTH_REGISTERED)
    
    # a value of 2047 means invalid measurement set these to zero to filter them from depth average
    depth[depth == 2047] = 0
    depth = depth.astype('float64') / 1000.
    return depth.sum() / np.count_nonzero(depth)
