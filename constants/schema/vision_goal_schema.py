from constants.schema.common import IMAGE_VECTORIZER, TEXT_VECTORIZER

PET_VIEW_WITH_GOAL_DB_SCHEMA_NAME = 'RoomViewSchemaWithGoal'
PET_VIEW_WITH_GOAL_CLASS_NAME = 'RoomWithGoalView'
PET_VIEW_WITH_GOAL_CLASS_SCHEMA = {
    "class": PET_VIEW_WITH_GOAL_CLASS_NAME,
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
            "description": "List of descriptions for all passageways in GPTPet's view"
        },
        {
            "name": "objects_descriptions",
            "dataType": ["string"],
            "description": "Summary of all objects in GPTPet's view"
        },
        {
            "name": "passageways",
            "dataType": ["string"],
            "description": "List of all passageways in GPTPet's view"
        },
        {
            "name": "goal_id",
            "dataType": ["string"],
            "description": "id of goal when gptpet generated this image description"
        }
    ]
}

# Define Goal class
GOAL_CLASS_NAME = 'Goal'

GOAL_CLASS_SCHEMA = {
    "class": GOAL_CLASS_NAME,
    "description": "A goal associated with multiple RoomViews",
    "vectorizer": TEXT_VECTORIZER,
    "properties": [
        {
            "name": "goal_text",
            "dataType": ["text"],
            "description": "The text describing the goal"
        },
        {
            "name": "completed",
            "dataType": ["boolean"],
            "description": "was the goal completed"
        }
    ]
}

# Define the complete schema with both classes
ROOM_VIEW_WITH_GOAL_VECTORDB_SCHEMA = {
    "name": PET_VIEW_WITH_GOAL_DB_SCHEMA_NAME,
    "classes": [
        PET_VIEW_WITH_GOAL_CLASS_SCHEMA,
        GOAL_CLASS_SCHEMA
    ]
}

