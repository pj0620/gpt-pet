from openai import OpenAI


class VisualLLMAdapterService:
  def __init__(self):
    self.client = OpenAI()
  
  def call_visual_llm(
      self,
      text_prompt: str,
      encoded_image_prompt: str
  ):
    response = self.client.chat.completions.create(
      model="gpt-4o",
      messages=[
        {
          "role": "user",
          "content": [
            {"type": "text", "text": text_prompt},
            {
              "type": "image_url",
              "image_url": {
                "url": f"data:image/jpeg;base64,{encoded_image_prompt}",
                "detail": "low"
              }
            }
          ],
        }
      ],
      max_tokens=300,
    )
    return response.choices[0].message.content
  
  def call_visual_llm_with_system_prompt(
      self,
      system_prompt: str,
      encoded_image_prompt: str,
      human_prompt: str = None
  ):
    human_content = [{
      "type": "image_url",
      "image_url": {
        "url": f"data:image/jpeg;base64,{encoded_image_prompt}",
        "detail": "high"
      }
    }]
    if human_prompt is None:
      human_content.append({"type": "text", "text": human_prompt})
    response = None
    for try_count in range(5):
      try:
        response = self.client.chat.completions.create(
          model="gpt-4o",
          messages=[
            {
              "role": "system",
              "content": [
                {"type": "text", "text": system_prompt}
              ],
            },
            {
              "role": "user",
              "content": human_content,
            }
          ],
          max_tokens=600,
        )
      except Exception as e:
        print(f'failed {try_count + 1} times to call visual llm', e)
    if response is None:
      raise Exception("Cannot connect to vision llm")
    return response.choices[0].message.content
