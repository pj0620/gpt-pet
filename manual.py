import time

from constants.motor import MOVE_AHEAD, MOVE_RIGHT, MOVE_LEFT, MOVE_BACK
from module.sensory.sim.ai2thor_camera_module import Ai2ThorCameraModule
from module.sensory.sim.ai2thor_depth_camera_module import Ai2ThorDepthCameraModule
from service.motor.physical.physical_motor_adapter import PhysicalMotorService
from service.motor.sim.ai2thor_motor_adapter import Ai2ThorMotorService
from service.sensor.physical.physical_proximity_sensor_adapter import PhysicalProximitySensorAdapter
from service.sensor.sim.ai2thor_proximity_sensor_adapter import Ai2thorProximitySensorAdapter
from service.sim_adapter import SimAdapter

from flask import Flask, jsonify, abort
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

test_env = 'physical'

if test_env == 'local':
  sim_adapter = SimAdapter()
  motor_adapter = Ai2ThorMotorService(sim_adapter)
  camera_module = Ai2ThorCameraModule(sim_adapter)
  depth_camera_module = Ai2ThorDepthCameraModule(sim_adapter)
  proximity_adapter = Ai2thorProximitySensorAdapter(sim_adapter)
else:
  motor_adapter = PhysicalMotorService()
  proximity_adapter = PhysicalProximitySensorAdapter()

print('stopping motors')
motor_adapter.stop()

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

@app.route('/proximity-measurements', methods=['GET'])
def distance():
    return jsonify(proximity_adapter.get_measurements())

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
    while True:
        time.sleep(1)
        print("working")
    
    
    # app.run(debug=True, port=5001, host='0.0.0.0')

