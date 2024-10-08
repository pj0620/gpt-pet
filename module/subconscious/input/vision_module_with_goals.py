import json
from json import JSONDecodeError

import numpy as np
from langchain.output_parsers import YamlOutputParser
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_openai import ChatOpenAI

from gptpet_context import GPTPetContext
from model.objects import Object, ObjectDescription
from model.passageway import Passageway, PassagewayDescription
from model.subconscious import ConsciousInput
from model.vision import PetViewDescription, PetViewSource, CreatePetViewWithGoalModel
from module.subconscious.input.base_subconscious_input_module import BaseSubconsciousInputModule
from service.object_permanence_service import ObjectPermanenceService
from service.vectordb_adapter_service import VectorDBAdapterService
from service.visual_llm_adapter_service import VisualLLMAdapterService
from utils.env_utils import check_env_flag
from utils.passageway_utils import merge_passageways
from utils.prompt_utils import load_prompt, encode_image_array
from utils.serialization import serialize_dataclasses, deserialize_dataclasses
from utils.vision_utils import label_passageways, add_horizontal_guide_encode

VISION_MODULE_SCHEMA = {
  "current_view_description": "a text description of what gptpet is currently seeing",
  "passageway_descriptions": "list of descriptions for all passageways in gptpet's view",
  "objects_descriptions": "summary of all objects in GPTPet's view",
  "seen_before": "has gptpet seen this view before. This can be used to decide if this area should be explored."
}
VISION_MODULE_DESCRIPTION = "Summary of GPTPet's vision."
VISION_MODULE_NAME = "vision_module"


class VisionModuleWithGoals(BaseSubconsciousInputModule):
  def __init__(
      self,
      vectordb_adapter_service: VectorDBAdapterService
  ):
    self.system_prompt = load_prompt('goal_aware_vision_module/system.txt')
    human_prompt_str = load_prompt('goal_aware_vision_module/human.txt')
    self.human_prompt = PromptTemplate.from_template(human_prompt_str)
    yaml_parser = YamlOutputParser(pydantic_object=PetViewDescription)
    self.object_permanence_service = ObjectPermanenceService(vectordb_adapter_service)
    vision_llm = ChatOpenAI(temperature=0, model="gpt-4o", max_tokens=1024)
    self.chain = vision_llm | yaml_parser
  
  
  def get_description_vectordb(
      self,
      context: GPTPetContext,
      base64_image: str,
      vectordb_adapter: VectorDBAdapterService
  ) -> tuple[None | dict[str, str], None | list[Passageway], None | list[Object], None | str]:
    """
    :param context: GPTPet context
    :param base64_image: base64 version of GPTPet's current view
    :param vectordb_adapter:
    :return: (view_description, passageways, objects, pet_view_id)
    """
    if check_env_flag('DISABLE_VISION_VECTORDB'):
      context.analytics_service.new_text(f"found DISABLE_VISION_VECTORDB=true, skipping check to see if gptpet has "
                                         f"seen this image before")
      return None, None, None, None
    
    similar_view = vectordb_adapter.get_similar_pet_views_with_goal(base64_image,
                                                                     context.goal_mixin.get_current_goal().goal_id)
    if similar_view is None:
      context.last_pet_view_id = None
      return None, None, None, None
    vectordb_petview_id = similar_view['_additional']['id']
    try:
      description = similar_view['description']
      
      passageways = deserialize_dataclasses(similar_view['passageways'], Passageway)
      passageway_descriptions = json.loads(similar_view['passageway_descriptions'])
      
      objects_descriptions = similar_view['objects_descriptions']
      objects = deserialize_dataclasses(objects_descriptions, Object)
      objects_mini = [
        dict(description=obj.description, name=obj.name, seen_before=obj.seen_before)
        for obj in objects
      ]
      
      context.analytics_service.new_text(f'found existing view in vectordb with id={vectordb_petview_id}')
      
      return dict(
        current_view_description=description,
        passageway_descriptions=passageway_descriptions,
        objects_descriptions=objects_mini
      ), passageways, objects, vectordb_petview_id
    except (JSONDecodeError, TypeError) as e:
      context.analytics_service.new_text(f'failed to parse existing view in vectordb with id={vectordb_petview_id}, '
                                         f'deleting and calling llm')
      print(e)
      vectordb_adapter.delete_pet_view(vectordb_petview_id)
      return None, None, None, None
  
  def get_description_llm(
      self,
      context: GPTPetContext,
      image_arr: np.array,
      depth_image_arr: np.array,
      visual_llm_adapter: VisualLLMAdapterService
  ) -> tuple[dict[str, str], list[Passageway], list[Object]]:
    
    # setup images for vision llm
    labeled_img, physical_passageways = label_passageways(image_arr, depth_image_arr)
    base64_image = add_horizontal_guide_encode(labeled_img)
    
    context.analytics_service.new_image(base64_image)
    
    msgs = [
      SystemMessage(content=self.system_prompt),
      HumanMessage(
        content=[
          {"type": "text", "text": self.human_prompt.format(current_goal=context.goal_mixin.get_current_goal().description)},
          {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
        ])
    ]
    parsed_response: PetViewDescription = self.chain.invoke(msgs)
    
    # setup passageways
    passageway_descriptions_pydantic = parsed_response.passageway_descriptions
    passageway_descriptions = [
      PassagewayDescription(
        color=p_des.color,
        name=p_des.name,
        description=p_des.description
      )
      for p_des in passageway_descriptions_pydantic
    ]
    passageways = merge_passageways(
      context=context,
      passageway_descriptions=passageway_descriptions,
      physical_passageways=physical_passageways
    )
    parsed_response.passageway_descriptions = [
      dict(
        name=passageway.name,
        description=passageway.description
      )
      for passageway in passageways
    ]
    
    # setup objects
    objects_response = parsed_response.objects_descriptions
    augmented_objects = self.object_permanence_service.augment_objects(
      context=context,
      objects_response=objects_response,
      image_width=image_arr.shape[1],
      depth_frame=depth_image_arr
    )
    
    return parsed_response.dict(), passageways, augmented_objects
  
  def get_description(
      self,
      context: GPTPetContext,
      image_arr: np.array,
      depth_image_arr: np.array
  ) -> tuple[dict[str, str], list[Passageway], list[Object]]:
    base64_image = encode_image_array(image_arr).decode('utf-8')
    # pet_view_description, passageways, objects, pet_view_id = None, None, None, None
    # check vectordb
    pet_view_description, passageways, objects, pet_view_id = self.get_description_vectordb(
      context,
      base64_image,
      context.vectordb_adapter
    )
    # re-augment object to have new fresh info from vectordb
    if objects is not None:
      base_objects = [
        ObjectDescription(
          # hack to reverse from angle -> pixel
          horz_location=(image_arr.shape[1] * float(obj.horizontal_angle)) / 70 + image_arr.shape[1] / 2,
          description=obj.description,
          name=obj.name
        )
        for obj in objects
      ]
      objects = self.object_permanence_service.augment_objects(
        context=context,
        objects_response=base_objects,
        image_width=image_arr.shape[1],
        depth_frame=depth_image_arr
      )
    
    # handle when this has not been seen before
    if pet_view_description is None:
      context.analytics_service.new_text(f'pet view not found in vectordb, calling llm')
      pet_view_description, passageways, objects = self.get_description_llm(
        context=context,
        image_arr=image_arr,
        depth_image_arr=depth_image_arr,
        visual_llm_adapter=context.visual_llm_adapter
      )
      print(f'creating following view with goal  in vectordb, goal={context.goal_mixin.get_current_goal()} {pet_view_description=} {passageways=}')
      context.analytics_service.new_text(f'creating pet view in vectordb')
      objects_dict = [
        dict(
          horizontal_angle=obj.horizontal_angle,
          object_distance=obj.object_distance,
          description=obj.description,
          name=obj.name,
          seen_before=obj.seen_before
        )
        for obj in objects
      ]
      vectordb_petview_id = context.vectordb_adapter.create_pet_view_with_goal(
        CreatePetViewWithGoalModel(
          description=pet_view_description['description'],
          passageway_descriptions=json.dumps(pet_view_description['passageway_descriptions']),
          objects_descriptions=json.dumps(objects_dict),
          passageways=serialize_dataclasses(passageways),
          image=base64_image,
          goal_id=context.goal_mixin.get_current_goal().goal_id
        )
      )
      context.last_pet_view = PetViewSource(
        pet_view_id=vectordb_petview_id,
        newly_created=True
      )
      context.analytics_service.new_text(f'created petview with id = {vectordb_petview_id}, '
                                         f'associated with goal = {context.goal_mixin.get_current_goal()}')
      
      # mark that this is the first time we have seen this view before
      pet_view_description["seen_before"] = "false"
    
    else:
      context.analytics_service.new_image(base64_image)
      # mark that this is has been seen before
      pet_view_description["seen_before"] = "true"
      context.last_pet_view = PetViewSource(
        pet_view_id=pet_view_id,
        newly_created=False
      )
    
    # only send needed fields to conscious inputs
    objects_mini = [
      dict(description=obj.description, name=obj.name, seen_before=obj.seen_before)
      for obj in objects
    ]
    pet_view_description["objects_descriptions"] = objects_mini
    
    return pet_view_description, passageways, objects
  
  def build_conscious_input(self, context: GPTPetContext) -> ConsciousInput:
    assert 'last_frame' in context.sensory_outputs, "last_frame must be in sensory_outputs"
    assert 'last_depth_frame' in context.sensory_outputs, "last_depth_frame must be in sensory_outputs"
    image_arr = context.sensory_outputs['last_frame']
    depth_image_arr = context.sensory_outputs['last_depth_frame']
    view_description, passageways, objects = self.get_description(
      image_arr=image_arr,
      depth_image_arr=depth_image_arr,
      context=context
    )
    context.passageways = passageways
    context.objects_in_view = objects
    
    return ConsciousInput(
      value=view_description,
      schema=VISION_MODULE_SCHEMA,
      description=VISION_MODULE_DESCRIPTION,
      name=VISION_MODULE_NAME
    )
