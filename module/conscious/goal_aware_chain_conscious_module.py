import json
import pprint
from datetime import datetime

import yaml
from langchain.chains.llm import LLMChain
from langchain.output_parsers import YamlOutputParser, OutputFixingParser
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, PromptTemplate, \
  SystemMessagePromptTemplate
from langchain_openai import ChatOpenAI

from gptpet_context import GPTPetContext
from model.conscious import NewTaskResponse, TaskDefinition, TaskResult, SavedTask, NewTaskResponseGoalIncluded
from model.subconscious import ConsciousInput
from module.conscious.base_conscious_module import BaseConsciousModule
from utils.conscious import task_response_mapper
from utils.prompt_utils import load_prompt, get_yaml


class GoalAwareChainConsciousModule(BaseConsciousModule):
  def __init__(self):
    llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
    self.prompt_human = PromptTemplate.from_template(
      load_prompt('conscious_chain_goal_aware/human.txt')
    )
    self.prompt_system = PromptTemplate.from_template(
      load_prompt('conscious_chain_goal_aware/system.txt')
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
    self.chain = LLMChain(
      llm=llm,
      prompt=prompt,
      verbose=True
    )
    
    parser_llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    yaml_parser = YamlOutputParser(pydantic_object=NewTaskResponseGoalIncluded)
    self.output_parser = OutputFixingParser.from_llm(parser=yaml_parser, llm=parser_llm)
  
  def generate_new_task(self, context: GPTPetContext) -> TaskDefinition:
    pprint.pprint({"conscious_inputs": [
      inp.value
      for inp in context.conscious_inputs
    ]})
    
    # todo: do we need to give the high level description of the input?
    # -> inp.description
    conscious_inputs_schema_str = {
      inp.name: inp.schema
      for inp in context.conscious_inputs
    }
    
    conscious_inputs_value_str = {
      inp.name: inp.value
      for inp in context.conscious_inputs
    }
    
    human_input = self.prompt_human.format(
      subconscious_info=get_yaml(conscious_inputs_value_str, True),
      time=str(datetime.now()),
      previous_tasks=get_yaml(self.tasks_history, True),
      current_goal=context.goal_mixin.get_current_goal().description,
      looking_direction=context.kinect_service.get_current_looking_direction()
    )
    system_input = self.prompt_system.format(
      subconscious_schema=get_yaml(conscious_inputs_schema_str, True)
    )
    
    context.analytics_service.new_text(f"calling conscious change with: {human_input}")
    
    response_str = self.chain.predict(
      human_input=human_input,
      system_input=system_input
    )
    
    response: NewTaskResponseGoalIncluded = self.output_parser.parse(text=response_str)
    new_task = task_response_mapper(str(conscious_inputs_value_str), response)
    if response.previous_goal_completed:
      context.analytics_service.new_text(f"completed previous goal {context.goal_mixin.get_current_goal()}")
    context.goal_mixin.update_goal(response.next_goal, response.previous_goal_completed)
    
    return new_task
  
  def report_task_result(self, task_definition: TaskDefinition, task_result: TaskResult):
    new_memory = dict(
      task=task_definition.task,
      reasoning=task_definition.reasoning,
      task_succeeded=task_result.success
    )
    if not task_result.success:
      new_memory["executor_output"] = task_result.executor_output
    self.tasks_history.insert(0, new_memory)
    if len(self.tasks_history) > 5:
      self.tasks_history.pop(0)
    
