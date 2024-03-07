from model.conscious import NewTaskResponse, TaskDefinition


def task_response_mapper(conscious_inputs_str: str, new_task_resp: NewTaskResponse) -> TaskDefinition:
  return TaskDefinition(
    input=conscious_inputs_str,
    task=new_task_resp.task,
    reasoning=new_task_resp.reasoning
  )
