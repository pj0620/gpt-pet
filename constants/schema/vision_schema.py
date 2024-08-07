from constants.schema.common import IMAGE_VECTORIZER

PET_VIEW_DB_SCHEMA_NAME = 'RoomViewSchema'
PET_VIEW_CLASS_NAME = 'RoomView'

PET_VIEW_CLASS_SCHEMA = {
  "class": PET_VIEW_CLASS_NAME,
  "description": "An image captured from GPTPet's vision",
  'vectorizer': IMAGE_VECTORIZER,
  'vectorIndexType': 'hnsw',
  'moduleConfig': {
      IMAGE_VECTORIZER: {
          'imageFields': [
              'image'
          ]
      }
  },
  "properties": [
    {
      'name': 'image',
      'dataType': ['blob']
    },
    {
      "name": "description",
      "dataType": ["string"],
      "description": "Description of this view"
    },
    {
      "name": "passageway_descriptions",
      "dataType": ["string"],
      "description": "list of descriptions for all passageways in gptpet's view"
    },
    {
      "name": "objects_descriptions",
      "dataType": ["string"],
      "description": "summary of all objects in GPTPet's view"
    },
    {
      "name": "passageways",
      "dataType": ["string"],
      "description": "list of all passageways in gptpet's view"
    }
  ]
}

ROOM_VIEW_VECTORDB_SCHEMA = {
  "name": PET_VIEW_DB_SCHEMA_NAME,
  "classes": [
    PET_VIEW_CLASS_SCHEMA
  ]
}
