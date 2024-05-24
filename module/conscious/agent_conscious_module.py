from langchain.agents import create_json_chat_agent, AgentExecutor
from langchain.chains import ConversationChain, LLMChain
from langchain.output_parsers import YamlOutputParser
from langchain.memory import ConversationBufferWindowMemory, ConversationBufferMemory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, MessagesPlaceholder, \
  HumanMessagePromptTemplate, PromptTemplate
from langchain_openai import ChatOpenAI

from gptpet_context import GPTPetContext
from model.conscious import NewTaskResponse, TaskDefinition, TaskResult
from module.conscious.base_conscious_module import BaseConsciousModule
from utils.conscious import task_response_mapper
from utils.prompt_utils import load_prompt
from datetime import datetime
import pprint


class AgentConsciousModule(BaseConsciousModule):
  def __init__(self):
    llm = ChatOpenAI(model="gpt-3.5-turbo-1106")
    # self.memory = ConversationBufferWindowMemory(k=2, memory_key="chat_history")
    self.prompt_human = PromptTemplate.from_template(load_prompt('conscious/human.txt'))
    prompt = ChatPromptTemplate.from_messages(
      [
        SystemMessage(
          content=load_prompt('conscious/system.txt')
        ),
        MessagesPlaceholder(
          variable_name="chat_history"
        ),
        HumanMessagePromptTemplate.from_template(
          "{human_input}"
        )
      ]
    )
    memory = ConversationBufferWindowMemory(k=2, memory_key="chat_history")
    self.chain = LLMChain(
      llm=llm,
      prompt=prompt,
      verbose=True,
      memory=memory
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
    
    human_input = self.prompt_human.format(
      subconscious_info=conscious_inputs_str,
      time=str(datetime.now())
    )
    
    response_str = self.chain.predict(human_input=human_input)
    
    # TODO: gracefully handle parsing errors
    response = self.output_parser.parse(text=response_str)
    
    return task_response_mapper(conscious_inputs_str, response)
  
  def report_task_result(self, task_definition: TaskDefinition, task_result: TaskResult):
    # self.memory.save_context({"input": task_definition.task}, {"output": str(task_result.success)})
    pass
  