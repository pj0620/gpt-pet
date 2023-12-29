from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class AuditEntity:
  createdAt: Any
  modifiedAt: Any
  lastAccessedAt: Any
  
  def build_dict(self):
    return {
      "createdAt": self.createdAt,
      "modifiedAt": self.modifiedAt,
      "lastAccessedAt": self.lastAccessedAt
    }
  
@dataclass
class NamedEntity(AuditEntity):
  name: str
  description: str
  
  def build_dict(self) -> Dict[str, str]:
    return {
      **super().build_dict(),
      "name": self.name,
      "description": self.description
    }

@dataclass
class Room(NamedEntity):
  pass
  
