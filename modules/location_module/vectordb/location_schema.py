from vectordb.constants import ROOM_CLASS_NAME, IMAGE_CLASS_NAME, LOCATION_DB_SCHEMA_NAME

AUDIT_FIELDS = [
  {
    "name": "createdAt",
    "dataType": ["date"],
    "description": "Date when the room was added"
  },
  {
    "name": "modifiedAt",
    "dataType": ["date"],
    "description": "Date when the room details were last modified"
  },
{
    "name": "lastAccessedAt",
    "dataType": ["date"],
    "description": "Date when the room details were last access from db"
  }
]

NAMED_ENTITY_FIELDS = [
  {
    "name": "name",
    "dataType": ["string"],
    "description": "The name of the room"
  },
  {
    "name": "description",
    "dataType": ["string"],
    "description": "The name of the room"
  }
]

IMAGE_CLASS_SCHEMA = {
  "class": IMAGE_CLASS_NAME,
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
    *NAMED_ENTITY_FIELDS,
    *AUDIT_FIELDS
  ]
}

ROOM_CLASS_SCHEMA = {
  "class": ROOM_CLASS_NAME,
  "description": "A room in a building",
  "properties": [
    {
      'name': 'image',
      'dataType': ['blob']
    },
    {
      "name": "images",
      "dataType": ["Image"],
      "description": "Images associated with this room"
    },
    *NAMED_ENTITY_FIELDS,
    *AUDIT_FIELDS
  ]
}

LOCATION_VECTORDB_SCHEMA = {
  "name": LOCATION_DB_SCHEMA_NAME,
  "classes": [
    ROOM_CLASS_SCHEMA,
    IMAGE_CLASS_SCHEMA
  ]
}
