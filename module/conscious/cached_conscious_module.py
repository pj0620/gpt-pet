import pprint

from gptpet_context import GPTPetContext
from model.conscious import TaskDefinition, TaskResult, SavedTask
from module.conscious.base_conscious_module import BaseConsciousModule


class CachedConsciousModule(BaseConsciousModule):
  def __init__(self, source_conscious_module: BaseConsciousModule):
    self.source_conscious_module = source_conscious_module
    self.was_task_cached: list[bool] = []
    self.last_task_failed = False
  
  def generate_new_task_cache(self, context) -> TaskDefinition | None:
    # last task failed, avoid usin cache to try and figure out how to fix it
    if self.last_task_failed:
      context.analytics_service.new_text("not using previous task since last task failed")
      return None
    
    # we used the cache for the last 5 tasks, give the llm a chance
    if len(self.was_task_cached) >= 5 and self.was_task_cached.count(True) >= 5:
      context.analytics_service.new_text("not using previous task since last 5 tasks all used the cache")
      return None
    
    last_pet_view = context.last_pet_view
    if last_pet_view.newly_created:
      context.analytics_service.new_text("not using previous task since this is a new view")
      return None
    
    task = context.vectordb_adapter.get_task(last_pet_view.pet_view_id)
    if task is None:
      context.analytics_service.new_text("could not find task for pet_view, using llm to create task")
      return None
    
    return TaskDefinition(
      task=task.task,
      reasoning=task.reasoning,
      input='unknown'
    )
  
  def generate_new_task(self, context: GPTPetContext) -> TaskDefinition:
    pprint.pprint({"conscious_inputs": [
      inp.value
      for inp in context.conscious_inputs
    ]})
    
    task = self.generate_new_task_cache(context)
    
    if task is None:
      self.push_task_source(False)
      task = self.source_conscious_module.generate_new_task(context)
      context.vectordb_adapter.create_task(SavedTask(
        pet_view_id=context.last_pet_view.pet_view_id,
        task=task.task,
        reasoning=task.reasoning
      ))
    else:
      self.push_task_source(True)
    
    return task
  
  def push_task_source(self, was_cache: bool):
    self.was_task_cached.append(was_cache)
    if len(self.was_task_cached) > 5:
      self.was_task_cached.pop(0)
  
  def report_task_result(self, task_definition: TaskDefinition, task_result: TaskResult):
    self.last_task_failed = task_result.success
    self.source_conscious_module.report_task_result(task_definition, task_result)
