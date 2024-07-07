MOVE_AHEAD = 'MoveAhead'
MOVE_BACK = 'MoveBack'
MOVE_LEFT = 'MoveLeft'
MOVE_RIGHT = 'MoveRight'

ROTATE_RIGHT = 'RotateRight'
ROTATE_LEFT = 'RotateLeft'

LINEAR_ACTIONS = [
  MOVE_AHEAD,
  MOVE_BACK,
  MOVE_LEFT,
  MOVE_RIGHT
]

ROTATE_ACTIONS = [
  ROTATE_RIGHT,
  ROTATE_LEFT
]

ALL_MOTOR_ACTIONS = [
  *LINEAR_ACTIONS,
  *ROTATE_ACTIONS
]

MIN_WALL_DIST = 0.25

DEPTH_SENSOR_STUCK_THRESHOLD = 0.1
