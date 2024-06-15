from langchain_core.prompts import ChatPromptTemplate

from model.conscious import NewTaskResponse, TaskDefinition
from model.subconscious import ConsciousInput
from module.subconscious.input.vision_module import VISION_MODULE_NAME


def task_response_mapper(conscious_inputs_str: str, new_task_resp: NewTaskResponse) -> TaskDefinition:
  return TaskDefinition(
    input=conscious_inputs_str,
    task=new_task_resp.task,
    reasoning=new_task_resp.reasoning
  )


# TODO: is it beneficial to throw this at a llm?
def simple_subconscious_observation_summarizer(conscious_inputs: list[ConsciousInput]) -> str:
  """
  :param conscious_inputs: list of raw conscious inputs
  :return: natural language text description of conscious inputs
  """
  current_view_description = None
  passageways_count = -1
  passageway_descriptions_str = None
  objects_count = -1
  objects_descriptions_str = None
  for conscious_input in conscious_inputs:
    if conscious_input.name != VISION_MODULE_NAME:
      continue
    
    current_view_description = None
    if "current_view_description" in conscious_input.value:
      current_view_description = conscious_input.value["current_view_description"]
    elif "description" in conscious_input.value:
      current_view_description = conscious_input.value["description"]
    passageway_descriptions = conscious_input.value["passageway_descriptions"]
    passageways_count = len(passageway_descriptions)
    passageway_descriptions_str = ".".join([p["description"] for p in passageway_descriptions])
    objects_descriptions = conscious_input.value["objects_descriptions"]
    objects_count = len(objects_descriptions)
    objects_descriptions_str = ".".join([o["description"] for o in objects_descriptions])
    
  summary = current_view_description
  
  if passageway_descriptions_str is not None:
    summary += f"I see {passageways_count} passageways in front of me. {passageway_descriptions_str}."
  if objects_descriptions_str is not None:
    summary += f"Additionally I see {objects_count} objects. {objects_descriptions_str}"
  
  return summary
  
  
  
  
  
