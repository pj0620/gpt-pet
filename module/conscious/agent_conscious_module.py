import json
import pprint
from datetime import datetime

import yaml
from langchain.chains.llm import LLMChain
from langchain.output_parsers import YamlOutputParser
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, PromptTemplate, \
  SystemMessagePromptTemplate
from langchain_openai import ChatOpenAI

from gptpet_context import GPTPetContext
from model.conscious import NewTaskResponse, TaskDefinition, TaskResult
from module.conscious.base_conscious_module import BaseConsciousModule
from utils.conscious import task_response_mapper
from utils.prompt_utils import load_prompt


class AgentConsciousModule(BaseConsciousModule):
  def __init__(self):
    llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
    self.prompt_human = PromptTemplate.from_template(
      load_prompt('conscious/human.txt')
    )
    self.prompt_system = PromptTemplate.from_template(
      load_prompt('conscious/system.txt')
    )
    self.tasks_history: list[dict] = []
    prompt = ChatPromptTemplate.from_messages(
      [
        SystemMessagePromptTemplate.from_template(
          '{system_input}',
          input_variables=['system_input']
        ),
        HumanMessagePromptTemplate.from_template(
          "{human_input}",
          input_varaibles=['human_input']
        )
      ],
    )
    # summary_prompt = PromptTemplate(
    #   input_variables=["summary", "new_lines"], template=load_prompt('conscious/summarizer.txt')
    # )
    # self.entity_memory = ConversationSummaryMemory(
    #   llm=ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0.2),
    #   # return_messages=True,
    #   max_token_limit=50,
    #   prompt=summary_prompt,
    #   ai_prefix='GPTPet'
    # )
    self.chain = LLMChain(
      llm=llm,
      prompt=prompt,
      verbose=True
    )
    self.output_parser = YamlOutputParser(pydantic_object=NewTaskResponse)
  
  def generate_new_task(self, context: GPTPetContext) -> TaskDefinition:
    # todo: do we need to give the high level description of the input?
    # -> inp.description
    conscious_inputs_schema_str = {
      inp.name: inp.schema
      for inp in context.conscious_inputs
    }
    
    conscious_inputs_value_str = {
      # inp.name: self.expand_json_lists(inp.value)
      inp.name: inp.value
      for inp in context.conscious_inputs
    }
    
    pprint.pprint({"conscious_inputs": [
      inp.value
      for inp in context.conscious_inputs
    ]})
    
    human_input = self.prompt_human.format(
      subconscious_info=self.get_yaml(conscious_inputs_value_str, True),
      time=str(datetime.now()),
      previous_tasks=self.get_yaml(self.tasks_history, True),
      # history_summary=self.entity_memory.buffer
    )
    system_input = self.prompt_system.format(
      subconscious_schema=self.get_yaml(conscious_inputs_schema_str, True)
    )
    
    context.analytics_service.new_text(f"calling conscious change with: {human_input}")
    
    response_str = self.chain.predict(
      human_input=human_input,
      system_input=system_input
    )
    
    # TODO: gracefully handle parsing errors
    response = self.output_parser.parse(text=response_str)
    
    return task_response_mapper(str(conscious_inputs_value_str), response)
  
  # def build_entity_memory_def(self, task_definition: TaskDefinition, task_result: TaskResult):
  #   task_input = f"`{task_definition.input}`"
  #   task_output = f"{{ task=`{task_definition.task}`, reasoning=`{task_definition.reasoning}` }}"
  #   return task_input, task_output
  
  def report_task_result(self, task_definition: TaskDefinition, task_result: TaskResult):
    # Not needed; no summary
    # task_input, task_output = self.build_entity_memory_def(task_definition, task_result)
    # self.entity_memory.save_context({"input": task_input}, {"output": task_output})
    self.tasks_history.append(dict(task=task_definition.task, reasoning=task_definition.reasoning,
                                   task_succeded=task_result.success))
    if len(self.tasks_history) > 5:
      self.tasks_history.pop(0)
      
  def expand_json_lists(self, possible_list: str):
    if possible_list[0] == '[':
      corrected_string_data = possible_list.replace("''", '"')
      return json.loads(corrected_string_data)
    else:
      return possible_list
  
  def get_yaml(self, data: dict | list, leading_tab=False):
    yaml_str = yaml.dump(data, default_flow_style=False, indent=2)
    if leading_tab:
      return '\n'.join(['  ' + line for line in yaml_str.split('\n')])
    else:
      return yaml_str
