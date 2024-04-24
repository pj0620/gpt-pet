from constants.motor import ROTATE_RIGHT, ROTATE_LEFT

TIME_DIVISION_STEP = 0.001
TIME_DIVISIONS_PER_SECOND = 1000

VERT_DUTY_CYCLE = 90
HORZ_DUTY_CYCLE = 50
ROT_DUTY_CYCLE = 50

INVERSE_ROTATE_ACTIONS = {
  ROTATE_RIGHT: ROTATE_LEFT,
  ROTATE_LEFT: ROTATE_RIGHT
}

FULL_TURN_DURATION = 1.0
HORZ_ONE_METER_DURATION = 1.0
VERT_ONE_METER_DURATION = 1.0
