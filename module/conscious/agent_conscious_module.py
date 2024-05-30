import pprint
from datetime import datetime
from typing import Tuple

from langchain.chains.llm import LLMChain
from langchain.memory import ConversationEntityMemory, ConversationSummaryBufferMemory, ConversationSummaryMemory
from langchain.output_parsers import YamlOutputParser
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, PromptTemplate
from langchain_openai import ChatOpenAI

from gptpet_context import GPTPetContext
from model.conscious import NewTaskResponse, TaskDefinition, TaskResult
from module.conscious.base_conscious_module import BaseConsciousModule
from utils.conscious import task_response_mapper
from utils.prompt_utils import load_prompt


class AgentConsciousModule(BaseConsciousModule):
  def __init__(self):
    llm = ChatOpenAI(model="gpt-3.5-turbo-1106")
    self.prompt_human = PromptTemplate.from_template(
      load_prompt('conscious/human.txt')
    )
    self.tasks_history: list[Tuple[TaskDefinition, TaskResult]] = []
    prompt = ChatPromptTemplate.from_messages(
      [
        SystemMessage(
          content=load_prompt('conscious/system.txt')
        ),
        HumanMessagePromptTemplate.from_template(
          "{human_input} \nSummary of current session: \n{entity_history}",
          input_varaibles=['human_input', 'entity_history']
        )
      ],
    )
    self.entity_memory = ConversationSummaryMemory(
      llm=llm,
      memory_key="entity_history",
      input_key="human_input",
      return_messages=True,
      max_token_limit=50
    )
    self.chain = LLMChain(
      llm=llm,
      prompt=prompt,
      verbose=True,
      memory=self.entity_memory
    )
    self.output_parser = YamlOutputParser(pydantic_object=NewTaskResponse)
  
  def generate_new_task(self, context: GPTPetContext) -> TaskDefinition:
    conscious_inputs_str = str([
      inp.__dict__
      for inp in context.conscious_inputs
    ])
    
    pprint.pprint({"conscious_inputs":  [
      inp.__dict__
      for inp in context.conscious_inputs
    ]})
    
    previous_tasks = [
      f"{{task=`{task_definition.task}` reasoning=`{task_definition.reasoning}` successful=`{task_result.success}`}}"
      for (task_definition, task_result) in self.tasks_history
    ]
    human_input = self.prompt_human.format(
      subconscious_info=conscious_inputs_str,
      time=str(datetime.now()),
      previous_tasks=previous_tasks,
      # entity_history=str(self.chain.memory.memory_variables)
    )
  
    response_str = self.chain.predict(
      human_input=human_input
    )
    
    # TODO: gracefully handle parsing errors
    response = self.output_parser.parse(text=response_str)
    
    return task_response_mapper(conscious_inputs_str, response)
  
  def report_task_result(self, task_definition: TaskDefinition, task_result: TaskResult):
    self.tasks_history.append((task_definition, task_result))
    if len(self.tasks_history) > 5:
      self.tasks_history.pop(0)
  