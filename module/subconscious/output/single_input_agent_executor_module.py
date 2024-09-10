from json import tool
from typing import Tuple

from langchain import hub
from langchain.output_parsers import BooleanOutputParser, YamlOutputParser
from langchain_core.agents import AgentAction
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate, SystemMessagePromptTemplate, MessagesPlaceholder, \
  HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent, AgentExecutor, initialize_agent, AgentType, \
  create_json_chat_agent, create_structured_chat_agent

from agent.executor_agent import create_executor_chat_agent
from gptpet_context import GPTPetContext
from model.conscious import TaskResult, TaskDefinition
from model.executor import SkillValidationResponse
from model.skill_library import SkillCreateModel
from module.subconscious.output.base_executor_module import BaseExecutorModule
from service.vectordb_adapter_service import VectorDBAdapterService
from tools.environment.environment_tool import EnvironmentTool
from utils.prompt_utils import load_prompt, load_control_primitives_context, get_yaml

NO_MATCHING_SKILL_MSG = "no matching skill"

class SingleInputAgentExecutorModule(BaseExecutorModule):
  
  def __init__(self, context: GPTPetContext):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    # llm = ChatAnthropic(
    #   temperature=0,
    #   model_name="claude-3-opus-20240229"
    # )
    self.environment_tool = EnvironmentTool(
      motor_adapter=context.motor_adapter,
      proximity_sensor_adapter=context.device_io_adapter,
      context=context
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
    
    system_validation_prompt = load_prompt('executor_single_input/skill_validation_system.txt')
    human_validation_prompt = load_prompt('executor_single_input/skill_validation_human.txt')
    validation_prompt = ChatPromptTemplate.from_messages([
      SystemMessagePromptTemplate(
        prompt=PromptTemplate(input_variables=['programs'], template=system_validation_prompt)),
      MessagesPlaceholder(variable_name='chat_history', optional=True),
      HumanMessagePromptTemplate(
        prompt=PromptTemplate(input_variables=['skill', 'task'], template=human_validation_prompt))
    ])
    validation_prompt = validation_prompt.partial(
      programs=self.get_programs()
    )
    bool_output_parser = YamlOutputParser(pydantic_object=SkillValidationResponse)
    
    self.validation_chain = validation_prompt | llm | bool_output_parser
  
  def get_programs(self, skills=None):
    if skills is None:
      skills = []
    base_skills = [
      "motor_control",
      "proximity_sensor",
      "passageways",
      "objects"
    ]
    programs = "\n\n".join(load_control_primitives_context(base_skills) + skills)
    return programs
  
  def execute_from_skill_manager(
      self,
      context: GPTPetContext,
      vectordb_adapter: VectorDBAdapterService,
      new_task: TaskDefinition
  ) -> Tuple[str | None, bool, str]:
    """
    :param context:
    :param new_task:
    :param vectordb_adapter: VectorDBAdapter
    :return: the skill, if skill was executed successfully using the skil in the skill library, reasoning that the skill
     does or does not complete the task
    """
    skills_from_skill_manager = vectordb_adapter.get_similar_skill(new_task, 0.9)
    print('skills_from_skill_manager: ', skills_from_skill_manager)
    if len(skills_from_skill_manager) == 0:
      return None, False, NO_MATCHING_SKILL_MSG
    
    skill = skills_from_skill_manager[0]
    context.analytics_service.new_text(f"found previously existing skill, {skill}")
    
    # TODO: grab k skills, and make it choose from the list of k or -1 if not meet the task
    validation_response: SkillValidationResponse = self.validation_chain.invoke(dict(
      skill=skill.code,
      task=new_task.task
    ))
    if not validation_response.solves_task:
      context.analytics_service.new_text(
        f"validation chain found previously existing skill `{skill}` does NOT complete "
        f"the task `{new_task.task}` rejecting. reasoning: {validation_response.reasoning}")
      return None, False, validation_response.reasoning
    
    print(f'executing code from skill manager')
    try:
      self.environment_tool.real_execute(code=skill.code)
      return skill.code, True, validation_response.reasoning
    except Exception as e:
      print('got exception while executing skill manager code, deleting from skill library', e)
      context.analytics_service.new_text(
        f"got exception while executing skill manager code, deleting from skill library")
      vectordb_adapter.delete_skill(skill)
      return skill.code, False, f"attempted to execute and got the following error: {e}"
  
  def execute(self, context: GPTPetContext, new_task: TaskDefinition) -> TaskResult:
    self.environment_tool.update_passageways(context.passageways)
    self.environment_tool.update_objects(context.objects_in_view)
    
    code, completed_from_skill, skill_reasoning = self.execute_from_skill_manager(context, context.vectordb_adapter, new_task)
    if completed_from_skill:
      context.analytics_service.new_text("task was completed successfuly using skill from skill library")
      return TaskResult(
        success=True,
        executor_output=code
      )
    
    conscious_input = dict(task=new_task.task)
    if skill_reasoning != NO_MATCHING_SKILL_MSG:
      conscious_input = {
        **conscious_input,
        "previously_attempted_code": code,
        "reason_code_invalid": skill_reasoning
      }
    context.analytics_service.new_text(f"no previous skill found matching new task, invoking executor agent with following")
    context.analytics_service.new_text(get_yaml(conscious_input))
    result = self.agent_executor.invoke(dict(
      input=get_yaml(conscious_input),
      chat_history=[],
    ))
    # hack to check if environment tool successfully executed
    last_step = result['intermediate_steps'][-1]
    if not isinstance(last_step, tuple) or len(last_step) != 2:
      raise ValueError("Each intermediate step should be a tuple of (AgentAction, str).")
    
    last_step_input, last_env_tool_resp = last_step
    if not isinstance(last_step_input, AgentAction) or not isinstance(last_env_tool_resp, str):
      raise ValueError("The last step does not contain a valid AgentAction and response string.")
  
    success = 'success!' in last_env_tool_resp
    executor_output = result['output'] if success else last_env_tool_resp
    task_result = TaskResult(
      success=success,
      executor_output=executor_output
    )
    if success:
      skill_create_model = SkillCreateModel(
        task=new_task.task,
        code=task_result.executor_output
      )
      context.analytics_service.new_text(f"creating following skill: {skill_create_model}")
      context.vectordb_adapter.create_skill(skill_create_model)
    
    return task_result
