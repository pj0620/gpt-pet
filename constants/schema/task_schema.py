from constants.schema.common import TEXT_VECTORIZER

TASK_DB_SCHEMA_NAME = 'TaskSchema'
TASK_CLASS_NAME = 'Task'

TASK_CLASS_SCHEMA = {
  "class": TASK_CLASS_NAME,
  "description": "A gptpet task",
  "vectorizer": TEXT_VECTORIZER,
  "properties": [
    {
      "name": "task",
      "dataType": ["string"],
      "description": "Description of task for executor",
      "moduleConfig": {
        TEXT_VECTORIZER: {
          "skip": True
        }
      }
    },
    {
      "name": "pet_view_id",
      "dataType": ["string"],
      "description": "Associated pet view id",
      "moduleConfig": {
        TEXT_VECTORIZER: {
          "skip": True
        }
      }
    },
    {
      "name": "reasoning",
      "dataType": ["string"],
      "description": "reasoning behind task",
      "moduleConfig": {
        TEXT_VECTORIZER: {
          "skip": True
        }
      }
    }
  ]
}

TASK_VECTORDB_SCHEMA = {
  "name": TASK_DB_SCHEMA_NAME,
  "classes": [
    TASK_CLASS_SCHEMA
  ]
}