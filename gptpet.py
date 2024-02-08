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
  def exist(self):
    while True:
      # get all sensor outputs from sensory modules
      for sensory_module in self.sensory_modules:
        sensory_module.build_subconscious_input()
        
      # build input to conscious module from subconscious modules
      conscious_input = {}
      for subconscious_module in self.subconscious_modules:
        module_output = subconscious_module.build_conscious_input()
        conscious_input = { **conscious_input, **module_output}
      
      print(conscious_input)
      
      sleep(1)