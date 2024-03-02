import base64
from io import BytesIO

import numpy as np
from transformers import BlipProcessor, BlipForQuestionAnswering

import requests
from PIL import Image
from service.vision_llm.base_visual_llm_adapter_service import BaseVisualLLMAdapterService


class LlavaVisualLLMAdapterService(BaseVisualLLMAdapterService):
  
  def __init__(self):
    # TODO:
    pass
    
  
  def call_visual_llm(
      self,
      text_prompt: str,
      encoded_image_prompt: str
  ) -> str:
    # TODO:
    return '{"description": "I see a room", "turn_percent": 0}'