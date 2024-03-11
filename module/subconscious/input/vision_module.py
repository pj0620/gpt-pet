import numpy as np
from langchain_core.prompts import ChatPromptTemplate

from gptpet_context import GPTPetContext
from model.subconscious import ConsciousInput
from model.vision import CreatePetViewModel, PetViewDescription, PhysicalPassagewayInfo
from module.subconscious.input.base_subconscious_input_module import BaseSubconsciousInputModule
from service.vectordb_adapter_service import VectorDBAdapterService
from service.visual_llm_adapter_service import VisualLLMAdapterService
from utils.prompt_utils import load_prompt, encode_image_array
from langchain_core.output_parsers import JsonOutputParser

from utils.serialization import serialize_dataclasses, deserialize_dataclasses
from utils.vision_utils import label_passageways

VISION_MODULE_SCHEMA = {
  "current_view_description": "a text description of what gptpet is currently seeing",
  "passageway_descriptions": "list of descriptions for all passageways in gptpet's view"
}

VISION_MODULE_DESCRIPTION = "Summary of GPTPet's vision."

class VisionModule(BaseSubconsciousInputModule):
  def __init__(self):
    self.system_prompt = load_prompt('vision_module/system.txt')
    human_prompt_str = load_prompt('vision_module/human.txt')
    self.human_prompt = ChatPromptTemplate.from_template(human_prompt_str)
    self.json_parser = JsonOutputParser(pydantic_object=PetViewDescription)
    
    
  def get_description_vectordb(
      self,
      base64_image: str,
      vectordb_adapter: VectorDBAdapterService
  ) -> tuple[None, None] | tuple[dict[str, str], list[PhysicalPassagewayInfo]]:
    vectordb_resp = vectordb_adapter.get_similar_pet_views(base64_image)
    if len(vectordb_resp) == 0:
      return None, None
    resp = vectordb_resp[0]
    description = resp['description']
    passageways = deserialize_dataclasses(resp['passageways'], PhysicalPassagewayInfo)
    passageway_descriptions = resp['passageway_descriptions']
    vectordb_petview_id = resp['_additional']['id']
    print(f'found existing view in vectordb with id={vectordb_petview_id}')
    return dict(
      current_view_description=description,
      passageway_descriptions=passageway_descriptions
    ), passageways
  
  
  def get_description_llm(
      self,
      image_arr: np.array,
      depth_image_arr: np.array,
      visual_llm_adapter: VisualLLMAdapterService
  ) -> tuple[dict[str, str], list[PhysicalPassagewayInfo]]:
    labeled_img, xs_info = label_passageways(image_arr, depth_image_arr)
    base64_image = encode_image_array(labeled_img).decode('utf-8')
    response_str = visual_llm_adapter.call_visual_llm_with_system_prompt(
      system_prompt=self.system_prompt,
      human_prompt="Please describe this image",
      encoded_image_prompt=base64_image
    )
    print("called LLM and found text_description = ", response_str)
    parsed_response = self.json_parser.parse(response_str)
    return parsed_response, xs_info
  
  
  def get_description(
      self,
      context: GPTPetContext,
      image_arr: np.array,
      depth_image_arr: np.array
  ) -> tuple[dict[str, str], list[PhysicalPassagewayInfo]]:
    base64_image = encode_image_array(image_arr).decode('utf-8')
    # check vectordb
    pet_view_description, xs_info = self.get_description_vectordb(base64_image, context.vectordb_adapter)
    if pet_view_description is None:
      print('pet view not found in vectordb, calling llm: ')
      pet_view_description, xs_info = self.get_description_llm(
        image_arr=image_arr,
        depth_image_arr=depth_image_arr,
        visual_llm_adapter=context.visual_llm_adapter
      )
      print(f'creating following view in vectordb, {pet_view_description=} {xs_info=}')
      vectordb_petview_id = context.vectordb_adapter.create_pet_view(
        CreatePetViewModel(
          description=pet_view_description['description'],
          passageway_descriptions=str(pet_view_description['passageway_descriptions']),
          passageways=serialize_dataclasses(xs_info),
          image=base64_image
        )
      )
      print(f'created petview with id = {vectordb_petview_id}')
    
    return pet_view_description, xs_info
  
  def build_conscious_input(self, context: GPTPetContext) -> ConsciousInput:
    assert 'last_frame' in context.sensory_outputs, "last_frame must be in sensory_outputs"
    assert 'last_depth_frame' in context.sensory_outputs, "last_depth_frame must be in sensory_outputs"
    image_arr = context.sensory_outputs['last_frame']
    depth_image_arr = context.sensory_outputs['last_depth_frame']
    view_description, xs_info = self.get_description(
      image_arr=image_arr,
      depth_image_arr=depth_image_arr,
      context=context
    )
    context.passageways = xs_info
    
    return ConsciousInput(
      value=view_description,
      schema=VISION_MODULE_SCHEMA,
      description=VISION_MODULE_DESCRIPTION
    )
  