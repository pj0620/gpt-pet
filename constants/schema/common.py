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

IMAGE_VECTORIZER = 'img2vec-neural'
TEXT_VECTORIZER = 'text2vec-openai'
