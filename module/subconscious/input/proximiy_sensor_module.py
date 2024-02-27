from gptpet_context import GPTPetContext
from model.subconscious import ConsciousInput
from model.vision import PetView
from module.subconscious.input.base_subconscious_input_module import BaseSubconsciousInputModule
from utils.prompt_utils import load_prompt, encode_image_array
from langchain_core.output_parsers import JsonOutputParser

PROXIMITY_SENSOR_MODULE_SCHEMA = {
  "right": "Approximate distance in meters from the robot to the nearest obstacle right of GPTPet.",
  "ahead": "Approximate distance in meters from the robot to the nearest obstacle ahead of GPTPet.",
  "left": "Approximate distance in meters from the robot to the nearest obstacle left of GPTPet.",
  "back": "Approximate distance in meters from the robot to the nearest obstacle to back of GPTPet."
}

PROXIMITY_SENSOR_MODULE_DESCRIPTION = "Summary of Proximity Sensors on GPTPet"


class ProximitySensorModule(BaseSubconsciousInputModule):
  def __init__(self):
    self.prompt = load_prompt('vision_module/describe_room.txt')
  
  def build_conscious_input(self, context: GPTPetContext) -> ConsciousInput:
    return ConsciousInput(
      value=context.proximity_sensor_adapter.get_measurements(),
      schema=PROXIMITY_SENSOR_MODULE_SCHEMA,
      description=PROXIMITY_SENSOR_MODULE_DESCRIPTION
    )
