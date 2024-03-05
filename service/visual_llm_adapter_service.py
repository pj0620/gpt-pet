from openai import OpenAI


class VisualLLMAdapterService:
  def __init__(self):
    self.client = OpenAI()
    
  def call_visual_llm(
      self,
      system_prompt: str,
      human_prompt: str,
      encoded_image_prompt: str
  ):
    response = self.client.chat.completions.create(
      model="gpt-4-vision-preview",
      messages=[
        {
          "role": "system",
          "content": system_prompt,
        },
        {
          "role": "user",
          "content": [
            {"type": "text", "text": human_prompt},
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
  
  