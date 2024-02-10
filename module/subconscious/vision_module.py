from gptpet_env import GPTPetEnv
from model.vision import PetView
from module.subconscious.base_subconscious_module import BaseSubconsciousModule
from utils.prompt_utils import load_prompt, encode_image_array
from langchain_core.output_parsers import JsonOutputParser


class VisionModule(BaseSubconsciousModule):
  def __init__(self):
    self.prompt = load_prompt('vision_module/describe_room.txt')
  
  def build_conscious_input(self, env: GPTPetEnv):
    base64_image = encode_image_array(env.sensory_outputs['last_frame']).decode('utf-8')
    
    # check vectordb
    vectordb_resp = env.vectordb_adapter.get_similar_pet_views(base64_image)
    if len(vectordb_resp) > 0:
      print('found existing description from vectordb: ', vectordb_resp)
      description = vectordb_resp[0]['description']
      turn_percent = vectordb_resp[0]['turn_percent']
    else:
      # not found in vectordb, so use Visual LLM
      text_description = env.visual_llm_adapter.call_visual_llm(
        text_prompt=self.prompt,
        encoded_image_prompt=base64_image
      )
      print("called LLM and found text_description = ", text_description)
      
      json_parser = JsonOutputParser()
      parsed_response = json_parser.parse(text_description)
      print("")
      description = parsed_response['description']
      turn_percent = int(parsed_response['turn_percent'])
    
      env.vectordb_adapter.create_pet_view(
        PetView(
          description=description,
          turn_percent=turn_percent,
          image=base64_image
        )
      )
    
    return dict(
      current_view_description=description,
      turn_percent=turn_percent
    )
  