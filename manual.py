import base64

from PIL import Image
import io
import base64

from constants.motor import MOVE_AHEAD, MOVE_RIGHT, MOVE_LEFT, MOVE_BACK, ROTATE_LEFT
from gptpet_context import GPTPetContext
from module.sensory.physical.physical_depth_camera_module import PhysicalDepthCameraModule
from module.sensory.sim.ai2thor_camera_module import Ai2ThorCameraModule
from module.sensory.sim.ai2thor_depth_camera_module import Ai2ThorDepthCameraModule
from service.device_io.sim.ai2thor_proximity_sensor_adapter import Ai2thorDeviceIOAdapter
from service.motor.sim.ai2thor_motor_adapter import Ai2ThorMotorService
from service.sim_adapter import SimAdapter

from flask import Flask, jsonify, abort, request
from flask_cors import CORS

from utils.vision_utils import add_horizontal_guide_encode

app = Flask(__name__)
CORS(app)

test_env = 'physical'

context = GPTPetContext()

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
  
  camera_module = PhysicalCameraModule()
  depth_camera_module = PhysicalDepthCameraModule()

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
  print("move request: ", direction)
  if direction not in ACTION_MAPPING.keys():
    abort(400, 'Invalid direction')
  action = ACTION_MAPPING[direction]
  result = motor_adapter.do_movement(action)
  return jsonify({'moved': result, 'direction': direction})


@app.route('/rotate/<degrees>', methods=['POST'])
def rotate(degrees: str):
  print("rotate request: ", degrees)
  try:
    num_degrees = float(degrees)
  except ValueError:
    abort(400, 'Invalid number of degrees: ' + degrees)
  result = motor_adapter.do_rotate(ROTATE_LEFT, num_degrees)
  return jsonify({'moved': result})


@app.route('/proximity-measurements', methods=['GET'])
def distance():
  print("proximity-measurements request")
  return jsonify(device_io_adapter.get_measurements())


@app.route('/color', methods=['POST'])
def set_color():
  print("set_color request")
  # Get the data from the request
  rgb_data = request.data.decode('utf-8').strip()
  device_io_adapter.set_color(rgb_data)
  
  return 'success'


@app.route('/current-view', methods=['GET'])
def current_view():
  print("current_view request")
  sensory_output = camera_module.build_subconscious_input(context)
  np_array = sensory_output['last_frame']
  
  # Convert the NumPy array to an image
  image = Image.fromarray(np_array)
  
  # Save the image to a bytes buffer instead of a file
  buffer = io.BytesIO()
  image.save(buffer, format="PNG")  # You can change PNG to JPEG, etc.
  
  # Retrieve the image bytes
  image_bytes = buffer.getvalue()
  
  # Encode the bytes in base64
  base64_bytes = base64.b64encode(image_bytes)
  
  # Convert bytes to a string for easier handling/storage/transmission
  base64_string = base64_bytes.decode('utf-8')
  
  return jsonify(dict(image=base64_string))


@app.route('/current-depth-view', methods=['GET'])
def current_depth_view():
  print("current_depth_view request")
  sensory_output = depth_camera_module.build_subconscious_input(context)
  np_array = sensory_output['last_depth_frame']
  
  # Convert the NumPy array to an image
  image = Image.fromarray(np_array)
  
  # Save the image to a bytes buffer instead of a file
  buffer = io.BytesIO()
  image.save(buffer, format="PNG")  # You can change PNG to JPEG, etc.
  
  # Retrieve the image bytes
  image_bytes = buffer.getvalue()
  
  # Encode the bytes in base64
  base64_bytes = base64.b64encode(image_bytes)
  
  # Convert bytes to a string for easier handling/storage/transmission
  base64_string = base64_bytes.decode('utf-8')
  
  return jsonify(dict(image=base64_string))


@app.route('/helloworld', methods=['GET'])
def hello_world():
  return 'Hello World'


if __name__ == '__main__':
  app.run(debug=False, port=5001, host='0.0.0.0')
