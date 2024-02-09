import base64

from openai import OpenAI

from gptpet_env import GPTPetEnv
from module.subconcious.base_subconscious_module import BaseSubconsciousModule
from service.vectordb_adapter_service import VectorDBAdapterService
from utils.prompt_utils import load_prompt, encode_image, encode_image_array


class VisionModule(BaseSubconsciousModule):
  def __init__(self):
    self.client = OpenAI()
    self.prompt = load_prompt('vision_module/describe_room.txt')
    
  def build_conscious_input(self, env: GPTPetEnv):
    print(f'{env.sensory_outputs=}')
    
    base64_image = encode_image_array(env.sensory_outputs['last_frame']).decode('utf-8')
    print(base64_image)
    
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
    
    print(response)
    
    return {
      "current_view": response.choices[0].message
    }
  
  def get_previously_seen(self):
  