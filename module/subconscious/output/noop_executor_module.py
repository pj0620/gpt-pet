from gptpet_context import GPTPetContext
from model.conscious import TaskResult, TaskDefinition
from module.subconscious.output.base_executor_module import BaseExecutorModule


class DummyExecutorModule(BaseExecutorModule):
  
  def execute(self, context: GPTPetContext, new_task: TaskDefinition) -> TaskResult:
    return TaskResult(
      success=True,
      executor_output="dummy output"
    )
