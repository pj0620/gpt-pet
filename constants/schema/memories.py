from constants.schema.common import TEXT_VECTORIZER

MEMORY_DB_SCHEMA_NAME = 'MemorySchema'
MEMORY_CLASS_NAME = 'Memory'

MEMORY_CLASS_SCHEMA = {
  "class": MEMORY_CLASS_NAME,
  "description": "A memory stored in gptpet",
  "vectorizer": TEXT_VECTORIZER,
  "properties": [
    {
      "name": "memory",
      "dataType": ["string"],
      "description": "memory content",
      "moduleConfig": {
        TEXT_VECTORIZER: {
        }
      }
    }
  ]
}

MEMORY_VECTORDB_SCHEMA = {
  "name": MEMORY_DB_SCHEMA_NAME,
  "classes": [
    MEMORY_CLASS_SCHEMA
  ]
}