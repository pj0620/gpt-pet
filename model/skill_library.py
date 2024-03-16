from dataclasses import dataclass


@dataclass(frozen=True)
class SkillCreateModel:
  task: str
  code: str

@dataclass(frozen=True)
class FoundSkill:
  task: str
  code: str
  score: float