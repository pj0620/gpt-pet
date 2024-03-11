# Serialization function with type hints
import json
from dataclasses import is_dataclass, asdict
from typing import List, Type, TypeVar

T = TypeVar('T')

def serialize_dataclasses(instances: List[T]) -> str:
  print('serializing ', instances)
  if len(instances) == 0:
    return "[]"
  if not instances or not all(is_dataclass(instance) for instance in instances):
    raise ValueError("All instances must be dataclasses.")
  return json.dumps([asdict(instance) for instance in instances])

# Deserialization function with type hints
def deserialize_dataclasses(json_str: str, cls: Type[T]) -> List[T]:
  dicts = json.loads(json_str)
  return [cls(**dict_) for dict_ in dicts]

