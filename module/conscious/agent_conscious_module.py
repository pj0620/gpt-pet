from langchain.agents import create_json_chat_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, MessagesPlaceholder, \
  HumanMessagePromptTemplate, PromptTemplate
from langchain_openai import ChatOpenAI

from gptpet_context import GPTPetContext
from model.task import TaskDefinition
from module.conscious.base_conscious_module import BaseConsciousModule
from utils.prompt_utils import load_prompt


class AgentConsciousModule(BaseConsciousModule):
  def __init__(self):
    llm = ChatOpenAI(model="gpt-3.5-turbo-1106")
    prompt_system = load_prompt('conscious/system.txt')
    prompt_human = load_prompt('conscious/human.txt')
    template = ChatPromptTemplate.from_messages([
      SystemMessagePromptTemplate(prompt=PromptTemplate(input_variables=[], template=prompt_system)),
      MessagesPlaceholder(variable_name='chat_history', optional=True),
      HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['input'], template=prompt_human)),
      MessagesPlaceholder(variable_name='agent_scratchpad')
    ])
    agent = create_json_chat_agent(llm, [], template)
    self.agent_executor = AgentExecutor(agent=agent, tools=[], verbose=True)
  
  def generate_new_task(self, context: GPTPetContext) -> TaskDefinition:
    conscious_inputs = context.conscious_inputs
    
    
    return TaskDefinition(
      name="walk_straight",
      description="move forward avoiding obstacles"
    )