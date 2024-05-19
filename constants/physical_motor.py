from constants.motor import ROTATE_RIGHT, ROTATE_LEFT, MOVE_AHEAD, MOVE_BACK, MOVE_LEFT, MOVE_RIGHT

TIME_DIVISION_STEP = 0.01
TIME_DIVISIONS_PER_SECOND = 100

VERT_DUTY_CYCLE_WIDTH = 6
VERT_CYCLE_ON = 3
HORZ_DUTY_CYCLE_WIDTH = 1
HORZ_CYCLE_ON = 1
ROT_DUTY_CYCLE_WIDTH = 10
ROT_CYCLE_ON = 5

INVERSE_ROTATE_ACTIONS = {
  ROTATE_RIGHT: ROTATE_LEFT,
  ROTATE_LEFT: ROTATE_RIGHT
}

FULL_TURN_DURATION = 2.17
HORZ_ONE_METER_DURATION = 0.5
VERT_ONE_METER_DURATION = 0.5

ACTION_TO_DIRECTION = {
  MOVE_AHEAD: 'ahead',
  MOVE_BACK: 'back',
  MOVE_LEFT: 'left',
  MOVE_RIGHT: 'right'
}