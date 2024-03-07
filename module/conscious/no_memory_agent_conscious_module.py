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
from utils.prompt_utils import load_prompt
from datetime import datetime
import pprint


class NoMemoryAgentConsciousModule(BaseConsciousModule):
  def __init__(self):
    llm = ChatOpenAI(model="gpt-3.5-turbo-1106")
    prompt_system = load_prompt('conscious_no_memory/system.txt')
    prompt_human = load_prompt('conscious_no_memory/human.txt')
    template = ChatPromptTemplate.from_messages([
      SystemMessagePromptTemplate(prompt=PromptTemplate(input_variables=[], template=prompt_system)),
      HumanMessagePromptTemplate(prompt=PromptTemplate(
        input_variables=['subconscious_info', 'time', 'completed_tasks_so_far', 'failed_tasks'],
        template=prompt_human
      ))
    ])
    output_parser = YamlOutputParser(pydantic_object=NewTaskResponse)
    self.chain = template | llm | output_parser
  
  def generate_new_task(self, context: GPTPetContext) -> TaskDefinition:
    conscious_inputs_str = str([
      inp.__dict__
      for inp in context.conscious_inputs
    ])
    
    pprint.pprint({"conscious_inputs": [
      inp.__dict__
      for inp in context.conscious_inputs
    ]})
    
    response = self.chain.invoke(dict(
      subconscious_info=conscious_inputs_str,
      time=str(datetime.now()),
      completed_tasks_so_far="[]",
      failed_tasks="[]"
    ))
    
    return task_response_mapper(response)