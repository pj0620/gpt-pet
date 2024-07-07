from json import tool

from langchain import hub
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate, SystemMessagePromptTemplate, MessagesPlaceholder, \
  HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent, AgentExecutor, initialize_agent, AgentType, \
  create_json_chat_agent, create_structured_chat_agent

from gptpet_context import GPTPetContext
from model.conscious import TaskResult, TaskDefinition
from module.subconscious.output.base_executor_module import BaseExecutorModule
from tools.environment.environment_tool import EnvironmentTool
from tools.motor_tool import MotorTool
from utils.prompt_utils import load_prompt, load_control_primitives_context


class AgentExecutorModule(BaseExecutorModule):
  
  def __init__(self, context: GPTPetContext):
    llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
    print('context.motor_service: ', context.motor_adapter)
    self.environment_tool = EnvironmentTool(
      motor_adapter=context.motor_adapter,
      proximity_sensor_adapter=context.device_io_adapter
    )
    tools = [ self.environment_tool ]
    prompt_system = load_prompt('executor/system.txt')
    prompt_human = load_prompt('executor/human.txt')
    prompt_human = prompt_human.replace("{programs}", self.get_programs())
    template = ChatPromptTemplate.from_messages([
      SystemMessagePromptTemplate(prompt=PromptTemplate(input_variables=['programs'], template=prompt_system)),
      MessagesPlaceholder(variable_name='chat_history', optional=True),
      HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['input'], template=prompt_human))
    ])
    agent = create_structured_chat_agent(llm, tools, template)
    self.agent_executor = AgentExecutor(
      agent=agent,
      tools=tools,
      verbose=True,
      handle_parsing_errors=True,
      max_iterations=5,
      return_intermediate_steps=True
    )
  
  def get_programs(self, skills=None):
    if skills is None:
      skills = []
    base_skills = [
      "motor_control",
      "proximity_sensor",
      "passageways"
    ]
    programs = "\n\n".join(load_control_primitives_context(base_skills) + skills)
    print('programs: ', programs)
    return programs
    
  def execute(self, context: GPTPetContext, new_task: TaskDefinition) -> TaskResult:
    self.environment_tool.update_passageways(context.passageways)
    
    result = self.agent_executor.invoke(dict(
      input=new_task,
      chat_history=[],
    ))
    print(result)
    return TaskResult(
      success=True,
      executor_output=str(result)
    )
  