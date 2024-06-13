import pprint
from datetime import datetime

from langchain.chains.llm import LLMChain
from langchain.output_parsers import YamlOutputParser
from langchain.retrievers import TimeWeightedVectorStoreRetriever
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, \
  HumanMessagePromptTemplate
from langchain_experimental.generative_agents import GenerativeAgentMemory
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

from gptpet_context import GPTPetContext
from model.conscious import TaskDefinition, TaskResult, NewTaskResponse
from module.conscious.base_conscious_module import BaseConsciousModule
from service.vectordb_adapter_service import VectorDBAdapterService
from utils.conscious import task_response_mapper, simple_subconscious_observation_summarizer
from utils.prompt_utils import load_prompt, get_yaml


class GenerativeAgentConsciousModule(BaseConsciousModule):
  def __init__(self, vector_db_adapter_service: VectorDBAdapterService):
    # setup gen agent memory
    retriever = TimeWeightedVectorStoreRetriever(
      vectorstore=vector_db_adapter_service.weaviate_memory_lc,
      # decay_rate=0.0000000000000000000000001,
      otherScoreKeys=["importance"],
      k=5
    )
    self.gen_memory = GenerativeAgentMemory(
      llm=ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0.5),
      memory_retriever=retriever,
      verbose=True,
    )
    self.subconscious_input_summarizer = simple_subconscious_observation_summarizer
    self.last_subconscious_summary = None
    
    # setup conscious chain
    llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
    self.prompt_human = PromptTemplate.from_template(
      load_prompt('conscious_genagent/human.txt')
    )
    self.prompt_system = PromptTemplate.from_template(
      load_prompt('conscious_genagent/system.txt')
    )
    # self.tasks_history: list[dict] = []
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
    self.output_parser = YamlOutputParser(pydantic_object=NewTaskResponse)
  
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
    
    self.last_subconscious_summary = self.subconscious_input_summarizer(
      context.conscious_inputs
    )
    print("conscious_input_summary: ", self.last_subconscious_summary)
    relevant_memories_docs = self.gen_memory.fetch_memories(self.last_subconscious_summary, datetime.now())
    relevant_memories_strs = [rm.page_content for rm in relevant_memories_docs]
    human_input = self.prompt_human.format(
      subconscious_info=get_yaml(conscious_inputs_value_str, True),
      time=str(datetime.now()),
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
    
    # TODO: gracefully handle parsing errors
    response = self.output_parser.parse(text=response_str)
    new_task = task_response_mapper(str(conscious_inputs_value_str), response)
    
    return new_task
  
  def report_task_result(self, task_definition: TaskDefinition, task_result: TaskResult) -> None:
    if self.last_subconscious_summary is None:
      return
    """ update task results for success or fail
    """
    success_str = ""
    if not task_result.success:
      success_str = "NOT"
      
    final_memory_summary = (
      f"After receiving the following context: {self.last_subconscious_summary}."
      f"GPTPet has decided to {task_definition.task} for the following reasoning. {task_definition.reasoning}."
      f"This task was {success_str} executed successfully"
    )
    self.gen_memory.add_memory(final_memory_summary)