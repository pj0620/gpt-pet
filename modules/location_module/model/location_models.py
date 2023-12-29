from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class AuditEntity:
  createdAt: Any
  modifiedAt: Any
  lastAccessedAt: Any
  
@dataclass(frozen=True)
class NamedEntity(AuditEntity):
  name: str
  description: str

@dataclass(frozen=True)
class Room(NamedEntity):
  pass

@dataclass(frozen=True)
class Image(AuditEntity):
  image: str
  pass
  
