from model.conscious import NewTaskResponse, TaskDefinition


def task_response_mapper(new_task_resp: NewTaskResponse) -> TaskDefinition:
  return TaskDefinition(
    task=new_task_resp.task,
    reasoning=new_task_resp.reasoning
  )
