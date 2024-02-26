from gptpet_context import GPTPetContext
from model.conscious import TaskDefinition
from module.conscious.base_conscious_module import BaseConsciousModule


class DummyConsciousModule(BaseConsciousModule):
  def generate_new_task(self, context: GPTPetContext) -> TaskDefinition:
    return TaskDefinition(
      task="walk straight",
      reasoning="looks cool over there, let's go that way"
    )