from gptpet_context import GPTPetContext
from model.task import TaskDefinition
from module.conscious.base_conscious_module import BaseConsciousModule


class DummyConsciousModule(BaseConsciousModule):
  def generate_new_task(self, context: GPTPetContext) -> TaskDefinition:
    return TaskDefinition(
      name="walk_straight",
      description="move forward avoiding obstacles"
    )