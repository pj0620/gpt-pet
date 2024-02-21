from gptpet_env import GPTPetEnv
from model.subconscious import ConsciousInput
from model.vision import PetView
from module.subconscious.input.base_subconscious_input_module import BaseSubconsciousInputModule
from utils.prompt_utils import load_prompt, encode_image_array
from langchain_core.output_parsers import JsonOutputParser

VISION_MODULE_SCHEMA = {
  "current_view_description": "a text description of what gptpet is currently seeing",
  "turn_percent": "an integer from -100 to 100 estimating how much the pet must turn if it wanted to move forward "
                  "and not hit anything."
}

VISION_MODULE_DESCRIPTION = "This conscious input represents all data from GPTPet's vision."

class VisionModule(BaseSubconsciousInputModule):
  def __init__(self):
    self.prompt = load_prompt('vision_module/describe_room.txt')
  
  def build_conscious_input(self, env: GPTPetEnv) -> ConsciousInput:
    base64_image = encode_image_array(env.sensory_outputs['last_frame']).decode('utf-8')
    
    # check vectordb
    vectordb_resp = env.vectordb_adapter.get_similar_pet_views(base64_image)
    if len(vectordb_resp) > 0:
      print('found existing description from vectordb: ', vectordb_resp)
      description = vectordb_resp[0]['description']
      turn_percent = vectordb_resp[0]['turn_percent']
      vectordb_petview_id = vectordb_resp[0]['_additional']['id']
    else:
      # not found in vectordb, so use Visual LLM
      text_description = env.visual_llm_adapter.call_visual_llm(
        text_prompt=self.prompt,
        encoded_image_prompt=base64_image
      )
      print("called LLM and found text_description = ", text_description)
      
      json_parser = JsonOutputParser()
      parsed_response = json_parser.parse(text_description)
      description = parsed_response['description']
      turn_percent = int(parsed_response['turn_percent'])
    
      vectordb_petview_id = env.vectordb_adapter.create_pet_view(
        PetView(
          description=description,
          turn_percent=turn_percent,
          image=base64_image
        )
      )
      print(f'created petview with id = {vectordb_petview_id}')
    
    return ConsciousInput(
      value=dict(
        current_view_description=description,
        turn_percent=turn_percent
      ),
      schema=VISION_MODULE_SCHEMA,
      description=VISION_MODULE_DESCRIPTION
    )
  