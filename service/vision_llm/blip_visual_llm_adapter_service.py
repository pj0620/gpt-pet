import base64
from io import BytesIO

import numpy as np
from transformers import BlipProcessor, BlipForQuestionAnswering

import requests
from PIL import Image
from service.vision_llm.base_visual_llm_adapter_service import BaseVisualLLMAdapterService


class BlipVisualLLMAdapterService(BaseVisualLLMAdapterService):
  
  def __init__(self):
    self.processor = BlipProcessor.from_pretrained("Salesforce/blip-vqa-base")
    self.model = BlipForQuestionAnswering.from_pretrained("Salesforce/blip-vqa-base")
    
  
  def call_visual_llm(
      self,
      text_prompt: str,
      encoded_image_prompt: str
  ) -> str:
    # Step 2: Decode the Base64 bytes to get the original binary image data
    img_data = base64.b64decode(encoded_image_prompt)
    
    # Step 3: Convert the binary data back into a NumPy array
    # Create a BytesIO object from the binary image data
    img_buffer = BytesIO(img_data)
    
    # Open the image with PIL and convert it to a NumPy array
    img = Image.open(img_buffer)
    img_array = np.array(img)
    
    inputs = self.processor(img_array, text_prompt, return_tensors="pt")
    
    out = self.model.generate(**inputs)
    return self.processor.decode(out[0], skip_special_tokens=True)