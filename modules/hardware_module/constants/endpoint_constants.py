from constants.ai2thor_constants import AI2THOR_MOVE_RIGHT, AI2THOR_MOVE_BACK, AI2THOR_MOVE_LEFT, AI2THOR_MOVE_AHEAD

BASE_ENDPOINT = '/environment'

FORWARD = 'forward'
LEFT = 'left'
BACK = 'back'
RIGHT = 'right'

VALID_MOVE_DIRECTIONS = [FORWARD, LEFT, BACK, RIGHT]
INVALID_DIRECTION_ERROR_MESSAGE = 'invalid direction: {}. Must be in the set of directions {}'
DIR_TO_AI2THOR_MOVEMENT = {
    FORWARD: AI2THOR_MOVE_AHEAD,
    LEFT: AI2THOR_MOVE_LEFT,
    BACK: AI2THOR_MOVE_BACK,
    RIGHT: AI2THOR_MOVE_RIGHT
}

INVALID_DEGREES_ERROR_MESSAGE = 'invalid turning degrees: {}'
