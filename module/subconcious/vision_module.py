from openai import OpenAI

from gptpet_env import GPTPetEnv
from model.vision import PetView
from module.subconcious.base_subconscious_module import BaseSubconsciousModule
from utils.prompt_utils import load_prompt, encode_image, encode_image_array


class VisionModule(BaseSubconsciousModule):
  def __init__(self):
    self.client = OpenAI()
    self.prompt = load_prompt('vision_module/describe_room.txt')
  
  def build_conscious_input(self, env: GPTPetEnv):
    base64_image = encode_image_array(env.sensory_outputs['last_frame']).decode('utf-8')
    
    # check vectordb
    vectordb_resp = env.vectordb_adapter_service.get_similar_pet_views(base64_image)
    if len(vectordb_resp) > 0:
      print('found existing description from vectordb: ', vectordb_resp)
      return {
        "current_view_description": vectordb_resp[0]['description']
      }
    
    # not found in vectordb, so use Visual LLM
    response = self.client.chat.completions.create(
      model="gpt-4-vision-preview",
      messages=[
        {
          "role": "user",
          "content": [
            {"type": "text", "text": self.prompt},
            {
              "type": "image_url",
              "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}",
                "detail": "low"
              }
            }
          ],
        }
      ],
      max_tokens=300,
    )
    text_description = response.choices[0].message.content
    print("called LLM and found text_description = ", text_description)
    
    env.vectordb_adapter_service.create_pet_view(
      PetView(
        description=text_description,
        image=base64_image
      )
    )
    
    return {
      "current_view_description": text_description
    }
  