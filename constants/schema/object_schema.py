from constants.schema.common import TEXT_VECTORIZER

OBJECT_DB_SCHEMA_NAME = 'ObjectSchema'
OBJECT_CLASS_NAME = 'Object'

OBJECT_CLASS_SCHEMA = {
  "class": OBJECT_CLASS_NAME,
  "description": "A object gptpet has found",
  "vectorizer": TEXT_VECTORIZER,
  "properties": [
    {
      "name": "object_name",
      "dataType": ["string"],
      "description": "Name of the object",
      "moduleConfig": {
        TEXT_VECTORIZER: {
          "skip": True
        }
      }
    },
    {
      "name": "object_description",
      "dataType": ["string"],
      "description": "Description of the object",
      "moduleConfig": {
        TEXT_VECTORIZER: {}
      }
    }
  ]
}

OBJECT_VECTORDB_SCHEMA = {
  "name": OBJECT_DB_SCHEMA_NAME,
  "classes": [
    OBJECT_CLASS_SCHEMA
  ]
}