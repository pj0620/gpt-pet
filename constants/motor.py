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

# depth sensor time threshold in seconds.
#   action with t < DEPTH_SENSOR_TIME_THRESHOLD -> NO depth sensor verification
#   action with t >= DEPTH_SENSOR_TIME_THRESHOLD -> depth sensor verification
DEPTH_SENSOR_TIME_THRESHOLD = 0.1

# depth sensor stuck threshold in percent.
#   percent change in avg depth < DEPTH_SENSOR_STUCK_THRESHOLD -> Stuck detected
#   percent change in avg depth >= DEPTH_SENSOR_STUCK_THRESHOLD -> NO Stuck detected
# DEPTH_SENSOR_STUCK_THRESHOLD = 0.05 # %

# depth sensor stuck threshold in mm.
#   change in avg depth < DEPTH_SENSOR_STUCK_THRESHOLD -> Stuck detected
#   change in avg depth >= DEPTH_SENSOR_STUCK_THRESHOLD -> NO Stuck detected
DEPTH_SENSOR_STUCK_THRESHOLD_MM = 20 # %
