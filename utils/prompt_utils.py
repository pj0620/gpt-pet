import base64


def load_prompt(prompt: str) -> str:
  with open('prompts/' + prompt) as f:
    return f.read()
  
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
  