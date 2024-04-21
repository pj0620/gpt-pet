from gptpet_context import GPTPetContext
from model.subconscious import ConsciousInput
from model.vision import CreatePetViewModel
from module.subconscious.input.base_subconscious_input_module import BaseSubconsciousInputModule
from utils.prompt_utils import load_prompt, encode_image_array
from langchain_core.output_parsers import JsonOutputParser

PROXIMITY_SENSOR_MODULE_SCHEMA = {
  "right": "distance to the right",
  "ahead": "distance to the ahead",
  "left": "distance to the left",
  "back": "distance to the back"
}

PROXIMITY_SENSOR_MODULE_DESCRIPTION = ("Summary of Proximity Sensors on GPTPet which reports approximate distance in "
                                       "meters to the nearest obstacle in each direction")


class ProximitySensorModule(BaseSubconsciousInputModule):
  def build_conscious_input(self, context: GPTPetContext) -> ConsciousInput:
    return ConsciousInput(
      value=context.device_io_adapter.get_measurements(),
      schema=PROXIMITY_SENSOR_MODULE_SCHEMA,
      description=PROXIMITY_SENSOR_MODULE_DESCRIPTION
    )
