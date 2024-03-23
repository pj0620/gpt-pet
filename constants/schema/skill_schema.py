from constants.schema.common import TEXT_VECTORIZER

SKILL_DB_SCHEMA_NAME = 'SkillSchema'
SKILL_CLASS_NAME = 'Skill'

SKILL_CLASS_SCHEMA = {
  "class": SKILL_CLASS_NAME,
  "description": "A gptpet skill",
  "vectorizer": TEXT_VECTORIZER,
  "properties": [
    {
      "name": "task",
      "dataType": ["string"],
      "description": "Description of task this skill solves",
      "moduleConfig": {
        TEXT_VECTORIZER: {}
      }
    },
    {
      "name": "code",
      "dataType": ["string"],
      "description": "Code for the skill",
      "moduleConfig": {
        TEXT_VECTORIZER: {
          "skip": True
        }
      }
    }
  ]
}

SKILL_VECTORDB_SCHEMA = {
  "name": SKILL_DB_SCHEMA_NAME,
  "classes": [
    SKILL_CLASS_SCHEMA
  ]
}