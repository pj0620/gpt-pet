import json

from gptpet_env import GPTPetEnv
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
  def exist(self, env: GPTPetEnv):
    while True:
      # get all sensor outputs from sensory modules
      env.sensory_outputs = {}
      for sensory_module in self.sensory_modules:
        env.sensory_outputs |= sensory_module.build_subconscious_input(env)
      
      print('env.sensory_outputs.keys(): ', env.sensory_outputs.keys())
        
      # build input to conscious module from subconscious modules
      env.subconscious_outputs = {}
      for subconscious_input_modules in self.subconscious_input_modules:
        env.subconscious_outputs |= subconscious_input_modules.build_conscious_input(env)
      
      print('env.subconscious_outputs: ', json.dumps(
        env.subconscious_outputs,
        sort_keys=True,
        indent=4,
        separators=(',', ': ')
      ))
      
      new_task = self.conscious_module.generate_new_task(env)
      
      print('new task: ', new_task)
      
      task_result = self.executor_module.execute(env, new_task)
      
      print('task_result: ', task_result)
      
      sleep(2)
      