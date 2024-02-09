import base64
from io import BytesIO

from PIL import Image


def load_prompt(prompt: str) -> str:
  with open('prompts/' + prompt) as f:
    return f.read()
  
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
  
def encode_image_array(image_arr):
  image = Image.fromarray(image_arr)
  buffer = BytesIO()
  image.save(buffer, format="JPEG")
  byte_data = buffer.getvalue()
  return base64.b64encode(byte_data)