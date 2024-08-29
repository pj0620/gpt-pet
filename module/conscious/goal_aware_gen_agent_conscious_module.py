import pprint
from datetime import datetime

from langchain.chains.llm import LLMChain
from langchain.output_parsers import YamlOutputParser, OutputFixingParser
from langchain.retrievers import TimeWeightedVectorStoreRetriever
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, PromptTemplate, \
  SystemMessagePromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_experimental.generative_agents import GenerativeAgentMemory
from langchain_openai import ChatOpenAI

from gptpet_context import GPTPetContext
from model.conscious import NewTaskResponse, TaskDefinition, TaskResult, SavedTask, NewTaskResponseGoalIncluded
from model.subconscious import ConsciousInput
from module.conscious.base_conscious_module import BaseConsciousModule
from service.analytics_service import AnalyticsService
from service.vectordb_adapter_service import VectorDBAdapterService
from utils.conscious import task_response_mapper, simple_subconscious_observation_summarizer
from utils.prompt_utils import load_prompt, get_yaml


class GoalAwareGenAgentChainConsciousModule(BaseConsciousModule):
  def __init__(
      self,
      vector_db_adapter_service: VectorDBAdapterService,
      analytics_service: AnalyticsService
  ):
    self.analytics_service = analytics_service
    llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
    self.prompt_human = PromptTemplate.from_template(
      load_prompt('conscious_goal_aware_gen_agent/human.txt')
    )
    self.prompt_system = PromptTemplate.from_template(
      load_prompt('conscious_goal_aware_gen_agent/system.txt')
    )
    self.tasks_history: list[dict] = []
    prompt = ChatPromptTemplate.from_messages(
      [
        SystemMessagePromptTemplate.from_template(
          '{system_input}',
          input_variables=['system_input']
        ),
        HumanMessagePromptTemplate.from_template(
          "{human_input}",
          input_varaibles=['human_input']
        )
      ],
    )
    self.chain = LLMChain(
      llm=llm,
      prompt=prompt,
      verbose=True
    )
    
    parser_llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    yaml_parser = YamlOutputParser(pydantic_object=NewTaskResponseGoalIncluded)
    self.output_parser = OutputFixingParser.from_llm(parser=yaml_parser, llm=parser_llm)
    
    # summarizer
    retriever = TimeWeightedVectorStoreRetriever(
      vectorstore=vector_db_adapter_service.weaviate_memory_lc,
      # decay_rate=0.0000000000000000000000001,
      otherScoreKeys=["importance"],
      k=5
    )
    self.gen_memory = GenerativeAgentMemory(
      llm=ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0.5),
      memory_retriever=retriever,
      reflection_threshold=0.25,
      verbose=True,
    )
    self.subconscious_input_summarizer = simple_subconscious_observation_summarizer
    self.last_subconscious_summary = None
    summarizer_prompt = ChatPromptTemplate.from_template(
      load_prompt("conscious_goal_aware_gen_agent/summarize.txt")
    )
    self.summarizer_chain = (
        {"observation": RunnablePassthrough()}
        | summarizer_prompt
        | ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        | StrOutputParser()
    )
  
  def generate_new_task(self, context: GPTPetContext) -> TaskDefinition:
    pprint.pprint({"conscious_inputs": [
      inp.value
      for inp in context.conscious_inputs
    ]})
    
    # todo: do we need to give the high level description of the input?
    # -> inp.description
    conscious_inputs_schema_str = {
      inp.name: inp.schema
      for inp in context.conscious_inputs
    }
    
    conscious_inputs_value_str = {
      inp.name: inp.value
      for inp in context.conscious_inputs
    }
    
    # Gen Agent
    self.last_subconscious_summary = self.subconscious_input_summarizer(
      context.conscious_inputs
    )
    context.analytics_service.new_text(f"conscious_input_summary: {self.last_subconscious_summary}")
    relevant_memories_docs = self.gen_memory.fetch_memories(self.last_subconscious_summary, datetime.now())
    relevant_memories_strs = [rm.page_content for rm in relevant_memories_docs]
    
    human_input = self.prompt_human.format(
      subconscious_info=get_yaml(conscious_inputs_value_str, True),
      time=str(datetime.now()),
      previous_tasks=get_yaml(self.tasks_history, True),
      current_goal=context.goal_mixin.get_current_goal().description,
      looking_direction=context.kinect_service.get_current_looking_direction(),
      relevant_memory=get_yaml(relevant_memories_strs, True),
    )
    system_input = self.prompt_system.format(
      subconscious_schema=get_yaml(conscious_inputs_schema_str, True)
    )
    
    context.analytics_service.new_text(f"calling conscious change with: {human_input}")
    
    response_str = self.chain.predict(
      human_input=human_input,
      system_input=system_input
    )
    
    response: NewTaskResponseGoalIncluded = self.output_parser.parse(response_str)
    new_task = task_response_mapper(str(conscious_inputs_value_str), response)
    if response.previous_goal_completed:
      context.analytics_service.new_text(f"completed previous goal {context.goal_mixin.get_current_goal()}")
    context.goal_mixin.update_goal(response.next_goal, response.previous_goal_completed)
    
    return new_task
  
  def report_task_result(self, task_definition: TaskDefinition, task_result: TaskResult):
    new_memory = dict(
      task=task_definition.task,
      reasoning=task_definition.reasoning,
      task_succeeded=task_result.success
    )
    if not task_result.success:
      new_memory["executor_output"] = task_result.executor_output
    self.tasks_history.insert(0, new_memory)
    if len(self.tasks_history) > 5:
      self.tasks_history.pop(0)
    
    # gen agent
    if self.last_subconscious_summary is None:
      return
    """ update task results for success or fail
    """
    success_str = ""
    if not task_result.success:
      success_str = "NOT "
    
    raw_observation_summary = (
      f"{self.last_subconscious_summary} "
      f"GPTPet has decided to {task_definition.task} for the following reasoning. {task_definition.reasoning}."
      f"This task was {success_str}executed successfully"
    )
    self.analytics_service.new_text(f"summarizing following raw observation: {raw_observation_summary}")
    compressed_memory_summary = self.summarizer_chain.invoke(raw_observation_summary)
    self.analytics_service.new_text(f"compressed observation: {compressed_memory_summary}")
    self.gen_memory.add_memory(compressed_memory_summary)
