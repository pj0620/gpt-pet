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
          "{human_input}",
          input_varaibles=['human_input']
        )
      ],
    )
    summary_prompt = PromptTemplate(
      input_variables=["summary", "new_lines"], template=load_prompt('conscious/summarizer.txt')
    )
    self.entity_memory = ConversationSummaryMemory(
      llm=ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0.2),
      # return_messages=True,
      max_token_limit=50,
      prompt=summary_prompt,
      ai_prefix='GPTPet'
    )
    self.chain = LLMChain(
      llm=llm,
      prompt=prompt,
      verbose=True
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
      # history_summary=self.entity_memory.buffer
    )
    
    context.analytics_service.new_text(f"calling conscious change with: {human_input}")
  
    response_str = self.chain.predict(
      human_input=human_input
    )
    
    # TODO: gracefully handle parsing errors
    response = self.output_parser.parse(text=response_str)
    
    return task_response_mapper(conscious_inputs_str, response)
  
  
  def build_entity_memory_def(self, task_definition: TaskDefinition, task_result: TaskResult):
    task_input = f"`{task_definition.input}`"
    task_output = f"{{ task=`{task_definition.task}`, reasoning=`{task_definition.reasoning}` }}"
    return task_input, task_output
  
  def report_task_result(self, task_definition: TaskDefinition, task_result: TaskResult):
    # Not needed; no summary
    # task_input, task_output = self.build_entity_memory_def(task_definition, task_result)
    # self.entity_memory.save_context({"input": task_input}, {"output": task_output})
    self.tasks_history.append((task_definition, task_result))
    if len(self.tasks_history) > 5:
      self.tasks_history.pop(0)
  