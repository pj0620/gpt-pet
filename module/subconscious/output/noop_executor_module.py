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


class DummyExecutorModule(BaseExecutorModule):
  
  def execute(self, env: GPTPetEnv, new_task: TaskDefinition) -> TaskResult:
    return TaskResult(
      success=True
    )
