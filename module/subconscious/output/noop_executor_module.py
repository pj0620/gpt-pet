from json import tool

from langchain import hub
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate, SystemMessagePromptTemplate, MessagesPlaceholder, \
  HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent, AgentExecutor, initialize_agent, AgentType, \
  create_json_chat_agent

from gptpet_context import GPTPetContext
from model.conscious import TaskResult, TaskDefinition
from module.subconscious.output.base_executor_module import BaseExecutorModule
from tools.motor_tool import MotorTool
from utils.prompt_utils import load_prompt


class DummyExecutorModule(BaseExecutorModule):
  
  def execute(self, context: GPTPetContext, new_task: TaskDefinition) -> TaskResult:
    return TaskResult(
      success=True
    )
