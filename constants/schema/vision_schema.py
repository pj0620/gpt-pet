PET_VIEW_DB_SCHEMA_NAME = 'RoomViewSchema'
PET_VIEW_CLASS_NAME = 'RoomView'

PET_VIEW_CLASS_SCHEMA = {
  "class": PET_VIEW_CLASS_NAME,
  "description": "An image captured from GPTPet's vision",
  'vectorizer': 'img2vec-neural',
  'vectorIndexType': 'hnsw',
  'moduleConfig': {
      'img2vec-neural': {
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
    }
  ]
}

ROOM_VIEW_VECTORDB_SCHEMA = {
  "name": PET_VIEW_DB_SCHEMA_NAME,
  "classes": [
    PET_VIEW_CLASS_SCHEMA
  ]
}
