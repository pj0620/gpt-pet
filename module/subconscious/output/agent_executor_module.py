from json import tool

from langchain import hub
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate, SystemMessagePromptTemplate, MessagesPlaceholder, \
  HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent, AgentExecutor, initialize_agent, AgentType, \
  create_json_chat_agent

from gptpet_env import GPTPetEnv
from model.task import TaskDefinition, TaskResult
from module.subconscious.output.base_executor_module import BaseExecutorModule
from tools.MotorTool import MotorTool
from utils.prompt_utils import load_prompt


class AgentExecutorModule(BaseExecutorModule):
  
  def __init__(self, env: GPTPetEnv):
    llm = ChatOpenAI(model="gpt-3.5-turbo-1106")
    print('env.motor_service: ', env.motor_service)
    tools = [
      MotorTool(env.motor_service)
    ]
    prompt_system = load_prompt('executor/system.txt')
    prompt_human = load_prompt('executor/human.txt')
    template = ChatPromptTemplate.from_messages([
      SystemMessagePromptTemplate(prompt=PromptTemplate(input_variables=[], template=prompt_system)),
      MessagesPlaceholder(variable_name='chat_history', optional=True),
      HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['input'], template=prompt_human)),
      MessagesPlaceholder(variable_name='agent_scratchpad')
    ])
    agent = create_json_chat_agent(llm, tools, template)
    self.agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
  def execute(self, env: GPTPetEnv, new_task: TaskDefinition) -> TaskResult:
    result = self.agent_executor.invoke(dict(
      input=new_task
    ))
    print(result)
    return TaskResult(
      success=True
    )
  