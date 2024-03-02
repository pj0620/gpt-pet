from abc import ABC


class BaseVisualLLMAdapterService(ABC):
  
  def call_visual_llm(
      self,
      text_prompt: str,
      encoded_image_prompt: str
  ) -> str:
    """
    :param text_prompt: prompt for vision LLM
    :param encoded_image_prompt: encoded image
    :return: string description from Vision-LLM
    """
    pass