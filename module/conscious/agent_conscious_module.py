from gptpet_env import GPTPetEnv
from model.task import TaskDefinition
from module.conscious.base_conscious_module import BaseConsciousModule


class AgentConsciousModule(BaseConsciousModule):
  def generate_new_task(self, env: GPTPetEnv) -> TaskDefinition:
    return TaskDefinition(
      name="walk_straight",
      description="move forward avoiding obstacles"
    )