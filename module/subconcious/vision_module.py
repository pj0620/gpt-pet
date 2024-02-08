from openai import OpenAI

from module.subconcious.base_subconscious_module import BaseSubconsciousModule
from utils.prompt_utils import load_prompt, encode_image


class VisionModule(BaseSubconsciousModule):
  def __init__(self):
    self.client = OpenAI()
    self.prompt = load_prompt('vision_module/describe_room.txt')
    
  def build_conscious_input(self):
    base64_image = encode_image('data/capture.jpeg')
    
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