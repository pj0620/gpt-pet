import json

from gptpet_env import GPTPetEnv
from module.conscious.base_conscious_module import BaseConsciousModule
from module.sensory.base_sensory_module import BaseSensoryModule
from module.subconscious.base_subconscious_module import BaseSubconsciousModule

from time import sleep


class GPTPet:
  def __init__(self,
     sensory_modules: list[BaseSensoryModule],
     subconscious_modules: list[BaseSubconsciousModule],
     conscious_modules: list[BaseConsciousModule]
  ):
    self.sensory_modules = sensory_modules
    self.subconscious_modules = subconscious_modules
    self.conscious_modules = conscious_modules
  def exist(self, env: GPTPetEnv):
    while True:
      # get all sensor outputs from sensory modules
      env.sensory_outputs = {}
      for sensory_module in self.sensory_modules:
        env.sensory_outputs |= sensory_module.build_subconscious_input(env)
      
      print('env.sensory_outputs.keys(): ', env.sensory_outputs.keys())
        
      # build input to conscious module from subconscious modules
      env.subconscious_outputs = {}
      for subconscious_module in self.subconscious_modules:
        env.subconscious_outputs |= subconscious_module.build_conscious_input(env)
      
      print('env.subconscious_outputs: ', json.dumps(
        env.subconscious_outputs,
        sort_keys=True,
        indent=4,
        separators=(',', ': ')
      ))
      
      results_info = {}
      for conscious_module in self.conscious_modules:
        results_info |= conscious_module.execute(env)
      
      print('results_info: ', json.dumps(
        results_info,
        sort_keys=True,
        indent=4,
        separators=(',', ': ')
      ))
      
      sleep(2)
      