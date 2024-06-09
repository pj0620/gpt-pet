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
from model.conscious import NewTaskResponse, TaskDefinition, TaskResult, SavedTask
from model.subconscious import ConsciousInput
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
    self.was_task_cached: list[bool] = []
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
    
  def generate_new_task_cache(self, context) -> TaskDefinition | None:
    # last task failed, avoid usin cache to try and figure out how to fix it
    if (len(self.tasks_history) > 0) and (not self.tasks_history[-1]['task_succeeded']):
      context.analytics_service.new_text("not using previous task since last task failed")
      return None
    
    # we used the cache for the last 5 tasks, give the llm a chance
    if len(self.was_task_cached) >= 5 and self.was_task_cached.count(True) >= 5:
      context.analytics_service.new_text("not using previous task since last 5 tasks all used the cache")
      return None
    
    last_pet_view = context.last_pet_view
    if last_pet_view.newly_created:
      context.analytics_service.new_text("not using previous task since this is a new view")
      return None

    task = context.vectordb_adapter.get_task(last_pet_view.pet_view_id)
    if task is None:
      context.analytics_service.new_text("could not find task for pet_view, using llm to create task")
      return None

    return TaskDefinition(
      task=task,
      reasoning=task.reasoning,
      input='unknown'
    )
    
  
  def generate_new_task_llm(self, context: GPTPetContext, conscious_inputs: list[ConsciousInput]) -> TaskDefinition:
    # todo: do we need to give the high level description of the input?
    # -> inp.description
    conscious_inputs_schema_str = {
      inp.name: inp.schema
      for inp in conscious_inputs
    }
    
    conscious_inputs_value_str = {
      # inp.name: self.expand_json_lists(inp.value)
      inp.name: inp.value
      for inp in conscious_inputs
    }
    
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
    new_task = task_response_mapper(str(conscious_inputs_value_str), response)
    
    context.vectordb_adapter.create_task(SavedTask(
      pet_view_id=context.last_pet_view.pet_view_id,
      task=new_task.task,
      reasoning=new_task.reasoning
    ))
    
    return new_task
  
  def generate_new_task(self, context: GPTPetContext) -> TaskDefinition:
    pprint.pprint({"conscious_inputs": [
      inp.value
      for inp in context.conscious_inputs
    ]})
    
    task = self.generate_new_task_cache(context)
    
    if task is None:
      task = self.generate_new_task_llm(context, context.conscious_inputs)
    
    return task
  
  # def build_entity_memory_def(self, task_definition: TaskDefinition, task_result: TaskResult):
  #   task_input = f"`{task_definition.input}`"
  #   task_output = f"{{ task=`{task_definition.task}`, reasoning=`{task_definition.reasoning}` }}"
  #   return task_input, task_output
  
  def push_task_source(self, was_cache: bool):
    self.was_task_cached.append(was_cache)
    if len(self.was_task_cached) > 5:
      self.was_task_cached.pop(0)
  
  def report_task_result(self, task_definition: TaskDefinition, task_result: TaskResult):
    # Not needed; no summary
    # task_input, task_output = self.build_entity_memory_def(task_definition, task_result)
    # self.entity_memory.save_context({"input": task_input}, {"output": task_output})
    self.tasks_history.append(dict(task=task_definition.task, reasoning=task_definition.reasoning,
                                   task_succeeded=task_result.success))
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
