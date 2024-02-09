from gptpet_env import GPTPetEnv
from module.sensory.base_sensory_module import BaseSensoryModule
from module.subconcious.base_subconscious_module import BaseSubconsciousModule

from time import sleep


class GPTPet:
  def __init__(self,
     sensory_modules: list[BaseSensoryModule],
     subconscious_modules: list[BaseSubconsciousModule]
  ):
    self.sensory_modules = sensory_modules
    self.subconscious_modules = subconscious_modules
  def exist(self, env: GPTPetEnv):
    while True:
      # get all sensor outputs from sensory modules
      env.sensory_outputs = {}
      for sensory_module in self.sensory_modules:
        env.sensory_outputs |= sensory_module.build_subconscious_input(env)
      
      print('env.sensory_outputs: ', env.sensory_outputs)
        
      # build input to conscious module from subconscious modules
      env.subconscious_outputs = {}
      for subconscious_module in self.subconscious_modules:
        env.subconscious_outputs |= subconscious_module.build_conscious_input(env)
      
      print('env.subconscious_outputs: ', env.subconscious_outputs)
      
      print(env.subconscious_outputs)
      
      sleep(1)
      