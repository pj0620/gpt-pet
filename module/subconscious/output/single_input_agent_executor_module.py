from json import tool
from typing import Tuple

from langchain import hub
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate, SystemMessagePromptTemplate, MessagesPlaceholder, \
  HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent, AgentExecutor, initialize_agent, AgentType, \
  create_json_chat_agent, create_structured_chat_agent

from agent.executor_agent import create_executor_chat_agent
from gptpet_context import GPTPetContext
from model.conscious import TaskResult, TaskDefinition
from model.skill_library import SkillCreateModel
from module.subconscious.output.base_executor_module import BaseExecutorModule
from service.vectordb_adapter_service import VectorDBAdapterService
from tools.environment.environment_tool import EnvironmentTool
from tools.motor_tool import MotorTool
from utils.prompt_utils import load_prompt, load_control_primitives_context


class SingleInputAgentExecutorModule(BaseExecutorModule):
  
  def __init__(self, context: GPTPetContext):
    llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)
    # llm = ChatAnthropic(
    #   temperature=0,
    #   model_name="claude-3-opus-20240229"
    # )
    self.environment_tool = EnvironmentTool(
      motor_adapter=context.motor_adapter,
      proximity_sensor_adapter=context.proximity_sensor_adapter
    )
    tools = [self.environment_tool]
    response_format = load_prompt('executor_single_input/response_format.txt')
    prompt_system = load_prompt('executor_single_input/system.txt')
    prompt_human = load_prompt('executor_single_input/human.txt')
    prompt = ChatPromptTemplate.from_messages([
      SystemMessagePromptTemplate(prompt=PromptTemplate(input_variables=['programs'], template=prompt_system)),
      MessagesPlaceholder(variable_name='chat_history', optional=True),
      HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['input'], template=prompt_human))
    ])
    prompt = prompt.partial(
      programs=self.get_programs(),
      response_format=response_format
    )
    agent = create_json_chat_agent(llm, tools, prompt)
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
    return programs
  
  def execute_from_skill_manager(
      self,
      vectordb_adapter: VectorDBAdapterService,
      new_task: TaskDefinition
  ) -> Tuple[str|None, bool]:
    """
    :param vectordb_adapter: VectorDBAdapter
    :return: the skill, and if skill was executed successfully using the skil in the skill library?
    """
    skills_from_skill_manager = vectordb_adapter.get_similar_skill(new_task, 0.9)
    print('skills_from_skill_manager: ', skills_from_skill_manager)
    if len(skills_from_skill_manager) == 0:
      return None, False
    
    skill = skills_from_skill_manager[0]
    print(f'executing code from skill manager')
    try:
      self.environment_tool.real_execute(code=skill.code)
      return skill.code, True
    except Exception as e:
      print('got exception while executing skill manager code, deleting from skill library', e)
      vectordb_adapter.delete_skill(skill)
      return skill.code, False
    
    
  def execute(self, context: GPTPetContext, new_task: TaskDefinition) -> TaskResult:
    self.environment_tool.update_passageways(context.passageways)
    
    code, completed_from_skill = self.execute_from_skill_manager(context.vectordb_adapter, new_task)
    if completed_from_skill:
      print("task was completed successfuly using skill from skill library")
      return TaskResult(
        success=True,
        final_code=code
      )
    
    result = self.agent_executor.invoke(dict(
      input=new_task.task,
      chat_history=[],
    ))
    # hack to check if environment tool successfully executed
    success = 'success!' in result['intermediate_steps'][-1][-1]
    task_result = TaskResult(
      success=success,
      final_code=result['output']
    )
    context.vectordb_adapter.create_skill(SkillCreateModel(
      task=new_task.task,
      code=task_result.final_code
    ))
    
    return task_result
  
  def save_skill(
      self,
      vectordb_adapter: VectorDBAdapterService,
      task: TaskDefinition,
      task_result: TaskResult
  ) -> None:
    vectordb_adapter.create_skill(SkillCreateModel(
      task=task.task,
      code=task_result.final_code
    ))
  