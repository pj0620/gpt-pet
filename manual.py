from constants.motor import MOVE_AHEAD, MOVE_RIGHT, MOVE_LEFT, MOVE_BACK
from module.sensory.sim.ai2thor_camera_module import Ai2ThorCameraModule
from module.sensory.sim.ai2thor_depth_camera_module import Ai2ThorDepthCameraModule
from module.sensory.sim.ai2thor_proximity_module import Ai2ThorProximityModule
from service.motor.physical.physical_motor_adapter import PhysicalMotorService
from service.motor.sim.ai2thor_motor_adapter import Ai2ThorMotorService
from service.sim_adapter import SimAdapter

from flask import Flask, jsonify, abort

app = Flask(__name__)

test_env = 'physical'

if test_env == 'local':
  sim_adapter = SimAdapter()
  motor_adapter = Ai2ThorMotorService(sim_adapter)
  camera_module = Ai2ThorCameraModule(sim_adapter)
  depth_camera_module = Ai2ThorDepthCameraModule(sim_adapter)
  proximity_module = Ai2ThorProximityModule(sim_adapter)
else:
  motor_adapter = PhysicalMotorService()
  
ACTION_MAPPING = dict(
  ahead=MOVE_AHEAD,
  right=MOVE_RIGHT,
  left=MOVE_LEFT,
  back=MOVE_BACK
)


@app.route('/move/<direction>', methods=['POST'])
def move(direction):
    if direction not in ACTION_MAPPING.keys():
        abort(400, 'Invalid direction')
    action = ACTION_MAPPING[direction]
    result = motor_adapter.do_movement(action)
    return jsonify({'moved': result, 'direction': direction})

# @app.route('/distance/<direction>', methods=['GET'])
# def distance(direction):
#     if direction not in ['forward', 'right', 'left', 'back', 'up', 'down']:
#         abort(400, 'Invalid direction')
#     dist = get_distance(direction)
#     return jsonify({'distance': dist, 'direction': direction})

# @app.route('/current-view', methods=['GET'])
# def current_view():
#     view = get_current_view()
#     return jsonify({'current_view': view})
#
# @app.route('/current-depth-view', methods=['GET'])
# def current_depth_view():
#     depth_view = get_current_depth_view()
#     return jsonify({'current_depth_view': depth_view})


if __name__ == '__main__':
    app.run(debug=True, port=5001)

