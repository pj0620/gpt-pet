import json

from chat.chat_agent import ChatAgent


class VisionService:
  def __init__(self):
    self.chat_agent = ChatAgent(chatgpt_model='gpt-4-vision-preview')
    
  def describe_room(self,
                    encoded_image: str = None) -> str:
    results = self.chat_agent.get_response_no_role(
      text_prompt="Generate a JSON object with two keys based on the room in the image. Only respond with json."
    "The keys should be:\n"
    "1. 'name': Suggest a suitable name for the room, like 'Blue Kitchen'.\n"
    "2. 'description': Provide a brief 2-3 sentence description of the room.",
      encoded_image=encoded_image
    )
    results = results.response_str.replace('\n', '').replace('\\','')
    
    return json.loads(self.trim_string_to_json_bounds(results))
  
  def trim_string_to_json_bounds(self, s: str) -> str:
    start_index = s.find('{')
    end_index = s.rfind('}')
    
    if start_index != -1 and end_index != -1 and end_index >= start_index:
      return s[start_index:end_index + 1]
    else:
      return "Invalid string format"