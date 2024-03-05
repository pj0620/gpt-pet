from langchain.agents import create_json_chat_agent, AgentExecutor
from langchain.output_parsers import YamlOutputParser
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, MessagesPlaceholder, \
  HumanMessagePromptTemplate, PromptTemplate
from langchain_openai import ChatOpenAI

from gptpet_context import GPTPetContext
from model.conscious import NewTaskResponse, TaskDefinition
from module.conscious.base_conscious_module import BaseConsciousModule
from utils.conscious import task_response_mapper
from utils.prompt_utils import load_prompt, encode_image_array
from datetime import datetime
import pprint


class AgentConsciousModule(BaseConsciousModule):
  def __init__(self):
    self.prompt_system = load_prompt('conscious/system.txt')
    prompt_human_raw = load_prompt('conscious/human.txt')
    self.prompt_human = PromptTemplate(
      input_variables=['subconscious_info', 'time', 'completed_tasks_so_far', 'failed_tasks'],
      template=prompt_human_raw
    )
    self.output_parser = YamlOutputParser(pydantic_object=NewTaskResponse)
    # self.chain = template | llm | output_parser
  
  def generate_new_task(self, context: GPTPetContext) -> TaskDefinition:
    conscious_inputs_str = str([
      inp.__dict__
      for inp in context.conscious_inputs
    ])
    
    pprint.pprint({"conscious_inputs":  [
      inp.__dict__
      for inp in context.conscious_inputs
    ]})
    
    human_prompt_inst = self.prompt_human.invoke(dict(
      subconscious_info=conscious_inputs_str,
      time=str(datetime.now()),
      completed_tasks_so_far="[]",
      failed_tasks="[]"
    )).to_string()
    
    base64_image = encode_image_array(context.sensory_outputs['last_frame']).decode('utf-8')
    context.visual_llm_adapter.call_visual_llm(
      system_prompt=self.prompt_system,
      human_prompt=human_prompt_inst,
      encoded_image_prompt=base64_image
    )
    
    # TODO:
    # response = self.chain.invoke(dict(
    #   subconscious_info=conscious_inputs_str,
    #   time=str(datetime.now()),
    #   completed_tasks_so_far="[]",
    #   failed_tasks="[]"
    # ))
    #
    return task_response_mapper(response)