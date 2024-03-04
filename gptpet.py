import json

from langchain_core.tracers.context import tracing_v2_enabled

from gptpet_context import GPTPetContext
from module.conscious.base_conscious_module import BaseConsciousModule
from module.sensory.base_sensory_module import BaseSensoryModule

from time import sleep

from module.subconscious.input.base_subconscious_input_module import BaseSubconsciousInputModule
from module.subconscious.output.base_executor_module import BaseExecutorModule


class GPTPet:
  def __init__(self,
     sensory_modules: list[BaseSensoryModule],
     subconscious_input_modules: list[BaseSubconsciousInputModule],
     conscious_module: BaseConsciousModule,
     executor_module: BaseExecutorModule
  ):
    self.sensory_modules = sensory_modules
    self.subconscious_input_modules = subconscious_input_modules
    self.conscious_module = conscious_module
    self.executor_module = executor_module
  def exist(self, context: GPTPetContext):
    with tracing_v2_enabled(project_name="gpt-pet"):
      while True:
        # get all sensor outputs from sensory modules
        context.sensory_outputs = {}
        for sensory_module in self.sensory_modules:
          context.sensory_outputs |= sensory_module.build_subconscious_input(context)
        
        print('context.sensory_outputs.keys(): ', context.sensory_outputs.keys())
        
        # build input to conscious module from subconscious modules
        context.conscious_inputs = []
        for subconscious_input_modules in self.subconscious_input_modules:
          context.conscious_inputs.append(subconscious_input_modules.build_conscious_input(context))
        
        print('context.conscious_inputs: ', context.conscious_inputs)
        
        new_task = self.conscious_module.generate_new_task(context)
        
        print('new task: ', new_task)
        
        task_result = self.executor_module.execute(context, new_task)
  
        print('task_result: ', task_result)
  
        sleep(2)
      