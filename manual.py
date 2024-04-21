import time

from pykinect2 import PyKinectRuntime, PyKinectV2

from constants.motor import MOVE_AHEAD, MOVE_RIGHT, MOVE_LEFT, MOVE_BACK
from module.sensory.sim.ai2thor_camera_module import Ai2ThorCameraModule
from module.sensory.sim.ai2thor_depth_camera_module import Ai2ThorDepthCameraModule
from service.device_io.sim.ai2thor_proximity_sensor_adapter import Ai2thorDeviceIOAdapter
from service.motor.sim.ai2thor_motor_adapter import Ai2ThorMotorService
from service.sim_adapter import SimAdapter

from flask import Flask, jsonify, abort, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

test_env = 'physical'

if test_env == 'local':
  sim_adapter = SimAdapter()
  motor_adapter = Ai2ThorMotorService(sim_adapter)
  camera_module = Ai2ThorCameraModule(sim_adapter)
  depth_camera_module = Ai2ThorDepthCameraModule(sim_adapter)
  device_io_adapter = Ai2thorDeviceIOAdapter(sim_adapter)
else:
  # keep imports here to avoid GPIO libraries causing issues
  from service.motor.physical.physical_motor_adapter import PhysicalMotorService
  from service.device_io.physical.physical_proximity_sensor_adapter import PhysicalDeviceIOAdapter
  from module.sensory.physical.physical_camera_module import PhysicalCameraModule
  motor_adapter = PhysicalMotorService()
  device_io_adapter = PhysicalDeviceIOAdapter()
  
  kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Depth)
  camera_module = PhysicalCameraModule(kinect)
  

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
    return jsonify(device_io_adapter.get_measurements())

@app.route('/color', methods=['POST'])
def set_color():
    # Get the data from the request
    rgb_data = request.data.decode('utf-8').strip()
    device_io_adapter.set_color(rgb_data)
    
    return 'success'

@app.route('/current-view', methods=['GET'])
def current_view():
    return jsonify(camera_module.build_subconscious_input())

# @app.route('/current-depth-view', methods=['GET'])
# def current_depth_view():
#     depth_view = get_current_depth_view()
#     return jsonify({'current_depth_view': depth_view})

@app.route('/helloworld', methods=['GET'])
def hello_world():
  return 'Hello World'


if __name__ == '__main__':
  app.run(debug=False, port=5001, host='0.0.0.0')

