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


class SingleInputAgentExecutorModule(BaseExecutorModule):
  
  def __init__(self, context: GPTPetContext):
    llm = ChatOpenAI(model="gpt-3.5-turbo-1106")
    print('context.motor_service: ', context.motor_adapter)
    tools = [
      EnvironmentTool(
        motor_adapter=context.motor_adapter,
        proximity_sensor_adapter=context.proximity_sensor_adapter
      )
    ]
    prompt_system = load_prompt('executor_single_input/system.txt')
    prompt_human = load_prompt('executor_single_input/human.txt')
    prompt_human = prompt_human.replace("{programs}", self.get_programs())
    template = ChatPromptTemplate.from_messages([
      SystemMessagePromptTemplate(prompt=PromptTemplate(input_variables=['programs'], template=prompt_system)),
      MessagesPlaceholder(variable_name='chat_history', optional=True),
      HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['input'], template=prompt_human))
    ])
    agent = create_json_chat_agent(llm, tools, template)
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
    # system_template = load_prompt("action_template")
    base_skills = [
      "motor_control",
      "proximity_sensor"
    ]
    programs = "\n\n".join(load_control_primitives_context(base_skills) + skills)
    # response_format = load_prompt("action_response_format")
    # system_message_prompt = SystemMessagePromptTemplate.from_template(
    #   system_template
    # )
    # system_message = system_message_prompt.format(
    #   programs=programs, response_format=response_format
    # )
    # assert isinstance(system_message, SystemMessage)
    return programs
  #
  # def render_human_message(
  #     self, *, events, code="", task="", context="", critique=""
  # ):
  #   chat_messages = []
  #   error_messages = []
  #   # FIXME: damage_messages is not used
  #   damage_messages = []
  #   assert events[-1][0] == "observe", "Last event must be observe"
  #   for i, (event_type, event) in enumerate(events):
  #     if event_type == "onChat":
  #       chat_messages.append(event["onChat"])
  #     elif event_type == "onError":
  #       error_messages.append(event["onError"])
  #     elif event_type == "onDamage":
  #       damage_messages.append(event["onDamage"])
  #     elif event_type == "observe":
  #       biome = event["status"]["biome"]
  #       time_of_day = event["status"]["timeOfDay"]
  #       voxels = event["voxels"]
  #       entities = event["status"]["entities"]
  #       health = event["status"]["health"]
  #       hunger = event["status"]["food"]
  #       position = event["status"]["position"]
  #       equipment = event["status"]["equipment"]
  #       inventory_used = event["status"]["inventoryUsed"]
  #       inventory = event["inventory"]
  #       assert i == len(events) - 1, "observe must be the last event"
  #
  #   observation = ""
  #
  #   if code:
  #     observation += f"Code from the last round:\n{code}\n\n"
  #   else:
  #     observation += f"Code from the last round: No code in the first round\n\n"
  #
  #   if self.execution_error:
  #     if error_messages:
  #       error = "\n".join(error_messages)
  #       observation += f"Execution error:\n{error}\n\n"
  #     else:
  #       observation += f"Execution error: No error\n\n"
  #
  #   if self.chat_log:
  #     if chat_messages:
  #       chat_log = "\n".join(chat_messages)
  #       observation += f"Chat log: {chat_log}\n\n"
  #     else:
  #       observation += f"Chat log: None\n\n"
  #
  #   observation += f"Biome: {biome}\n\n"
  #
  #   observation += f"Time: {time_of_day}\n\n"
  #
  #   if voxels:
  #     observation += f"Nearby blocks: {', '.join(voxels)}\n\n"
  #   else:
  #     observation += f"Nearby blocks: None\n\n"
  #
  #   if entities:
  #     nearby_entities = [
  #       k for k, v in sorted(entities.items(), key=lambda x: x[1])
  #     ]
  #     observation += f"Nearby entities (nearest to farthest): {', '.join(nearby_entities)}\n\n"
  #   else:
  #     observation += f"Nearby entities (nearest to farthest): None\n\n"
  #
  #   observation += f"Health: {health:.1f}/20\n\n"
  #
  #   observation += f"Hunger: {hunger:.1f}/20\n\n"
  #
  #   observation += f"Position: x={position['x']:.1f}, y={position['y']:.1f}, z={position['z']:.1f}\n\n"
  #
  #   observation += f"Equipment: {equipment}\n\n"
  #
  #   if inventory:
  #     observation += f"Inventory ({inventory_used}/36): {inventory}\n\n"
  #   else:
  #     observation += f"Inventory ({inventory_used}/36): Empty\n\n"
  #
  #   if not (
  #       task == "Place and deposit useless items into a chest"
  #       or task.startswith("Deposit useless items into the chest at")
  #   ):
  #     observation += self.render_chest_observation()
  #
  #   observation += f"Task: {task}\n\n"
  #
  #   if context:
  #     observation += f"Context: {context}\n\n"
  #   else:
  #     observation += f"Context: None\n\n"
  #
  #   if critique:
  #     observation += f"Critique: {critique}\n\n"
  #   else:
  #     observation += f"Critique: None\n\n"
  #
  #   return HumanMessage(content=observation)
    
  def execute(self, context: GPTPetContext, new_task: TaskDefinition) -> TaskResult:
    result = self.agent_executor.invoke(dict(
      input=new_task,
      chat_history=[],
    ))
    print(result)
    return TaskResult(
      success=True
    )
  