import itertools
import json
from time import sleep

import RPi.GPIO as GPIO

from constants.gpio.gpio_constants import FORWARD, FACES, SIDES, BACK, DIRECTIONS, BACKWARD, FRONT, LEFT, RIGHT
from constants.motor import LINEAR_ACTIONS, MOVE_AHEAD, MOVE_BACK, MOVE_LEFT, MOVE_RIGHT, ROTATE_ACTIONS, ROTATE_RIGHT, \
  ROTATE_LEFT
from constants.physical_motor import *
from model.motor import MovementResult
from service.motor.base_motor_adapter import BaseMotorAdapter

GPIO.setmode(GPIO.BOARD)
with open('constants/gpio/gpio.json', 'r') as file:
  gpio = json.load(file)

class PhysicalMotorService(BaseMotorAdapter):
  def __init__(self):
    with open('constants/gpio/gpio.json', 'r') as file:
      self.gpio = json.load(file)
  
  def do_movement(
      self,
      action: str,
      move_magnitude: float = 1
  ) -> MovementResult:
    assert action in LINEAR_ACTIONS, f'invalid movement action {action}'
    
    duty_cycle_width = HORZ_DUTY_CYCLE_WIDTH
    cycle_on = HORZ_CYCLE_ON
    if action == MOVE_AHEAD:
      duty_cycle_width = VERT_DUTY_CYCLE_WIDTH
      cycle_on = VERT_CYCLE_ON
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
    
    self.power_pins(on_pins, off_pins, duty_cycle_width, cycle_on, move_magnitude)
    
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
  
  def do_rotate(
      self,
      action: str,
      degrees: float = None
  ) -> MovementResult:
    assert action in ROTATE_ACTIONS, f'invalid rotate action {action}'
    
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
    
    duration = (degrees / 360.) * FULL_TURN_DURATION
    self.power_pins(on_pins, off_pins, ROT_DUTY_CYCLE_WIDTH, ROT_CYCLE_ON, duration)
    
    return MovementResult(
      successful=True,
      action=action,
      degrees=degrees
    )
  
  
  def power_pins(
      self,
      on_pins: list[int],
      off_pins: list[int],
      duty_cycle_width: int,
      cycle_on: int,
      duration: float
  ):
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
      sleep(TIME_DIVISION_STEP)
    
    for p in on_pins:
      GPIO.output(p, GPIO.LOW)
    
    GPIO.cleanup()
