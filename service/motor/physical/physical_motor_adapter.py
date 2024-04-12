import itertools
import json
from time import sleep

import RPi.GPIO as GPIO

from constants.gpio.gpio_constants import FORWARD, FACES, SIDES, BACK
from constants.motor import LINEAR_ACTIONS, MOVE_AHEAD, MOVE_BACK
from model.motor import MovementResult
from service.motor.base_motor_adapter import BaseMotorAdapter

GPIO.setmode(GPIO.BOARD)


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

    if action == MOVE_AHEAD:
      on_pins = [
        self.gpio[face][side][FORWARD]
        for face, side in itertools.product(FACES, SIDES)
      ]
      off_pins = [
        self.gpio[face][side][BACK]
        for face, side in itertools.product(FACES, SIDES)
      ]
    elif action == MOVE_BACK:
      on_pins = [
        self.gpio[face][side][BACK]
        for face, side in itertools.product(FACES, SIDES)
      ]
      off_pins = [
        self.gpio[face][side][FORWARD]
        for face, side in itertools.product(FACES, SIDES)
      ]
    else:
      raise Exception('Not implemented')
    
    for p in off_pins:
      GPIO.setup(p, GPIO.OUT, initial=GPIO.LOW)
      GPIO.output(p, GPIO.LOW)
    
    for p in on_pins:
      GPIO.setup(p, GPIO.OUT, initial=GPIO.LOW)
      GPIO.output(p, GPIO.HIGH)
      
    sleep(1)
    
    for p in on_pins:
      GPIO.output(p, GPIO.LOW)
    
    return MovementResult(
      successful=True,
      action=action,
    )

  # def do_rotate(
  #     self,
  #     action: str,
  #     degrees: float = None
  # ) -> MovementResult:
  #   assert action in ROTATE_TO_AI2THOR_ROTATE.keys(), f'invalid rotate action {action}'
  #
  #   self.sim_adapter.do_step(
  #     action=ROTATE_TO_AI2THOR_ROTATE[action],
  #     degrees=degrees
  #   )
  #
  #   if self.sim_adapter.last_event_successful():
  #     return MovementResult(
  #       successful=True,
  #       action=action,
  #       degrees=degrees
  #     )
  #   else:
  #     return MovementResult(
  #       successful=False,
  #       action=action,
  #     )
  
