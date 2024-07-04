import argparse
import base64
import pickle
import zlib

import cv2
import numpy as np
from dotenv import load_dotenv
from flask import Flask, jsonify, abort, request
from flask_cors import CORS

from constants.motor import MOVE_AHEAD, MOVE_RIGHT, MOVE_LEFT, MOVE_BACK, ROTATE_LEFT
from gptpet_context import GPTPetContext
from model.conscious import TaskDefinition
from module.sensory.sim.ai2thor_camera_module import Ai2ThorCameraModule
from module.sensory.sim.ai2thor_depth_camera_module import Ai2ThorDepthCameraModule
from module.subconscious.output.single_input_agent_executor_module import SingleInputAgentExecutorModule
from service.analytics_service import AnalyticsService
from service.device_io.sim.ai2thor_device_io_adapter import Ai2thorDeviceIOAdapter
from service.motor.sim.ai2thor_motor_adapter import Ai2ThorMotorService
from service.sim_adapter import SimAdapter
from service.tilt.sim.noop_tilt_service import NoopTiltService
from service.kinect.sim.noop_kinect_service import NoopKinectService
from service.vectordb_adapter_service import VectorDBAdapterService
from service.visual_llm_adapter_service import VisualLLMAdapterService
from utils.env_utils import get_env
from utils.vision_utils import add_horizontal_guide_encode, np_img_to_base64, label_passageways

load_dotenv()

app = Flask(__name__)
CORS(app)

# setup vectordb
context = GPTPetContext()
context.analytics_service = AnalyticsService()
context.vectordb_adapter = VectorDBAdapterService(context.analytics_service)
context.visual_llm_adapter = VisualLLMAdapterService()

if get_env() == 'local':
  sim_adapter = SimAdapter()
  motor_adapter = Ai2ThorMotorService(sim_adapter)
  camera_module = Ai2ThorCameraModule(sim_adapter)
  kinect_service = NoopKinectService()
  depth_camera_module = Ai2ThorDepthCameraModule(sim_adapter)
  device_io_adapter = Ai2thorDeviceIOAdapter(sim_adapter)
  tilt_service = NoopTiltService()
else:
  print('importing stuff')
  # keep imports here to avoid GPIO libraries causing issues
  from service.motor.physical.physical_motor_adapter import PhysicalMotorService
  from service.device_io.physical.physical_device_io_adapter import PhysicalDeviceIOAdapter
  from service.kinect.physical.async_physical_kinect_service import AsyncPhysicalKinectService
  from module.sensory.physical.async_physical_camera_module import AsyncPhysicalCameraModule
  from module.sensory.physical.async_physical_depth_camera_module import AsyncPhysicalDepthCameraModule
  
  print('setting up device_io_adapter')
  device_io_adapter = PhysicalDeviceIOAdapter()
  
  print('setting up AsyncPhysicalKinectService')
  kinect_service = AsyncPhysicalKinectService()
  
  print('setting up camera/depth camera modules')
  camera_module = AsyncPhysicalCameraModule(kinect_service)
  depth_camera_module = AsyncPhysicalDepthCameraModule(kinect_service)
  
  print('setting up motor adapter')
  motor_adapter = PhysicalMotorService(context=context)

context.motor_adapter = motor_adapter
context.device_io_adapter = device_io_adapter

print('stopping motors')
motor_adapter.stop()
motor_adapter.setup_motors()

executor = SingleInputAgentExecutorModule(context)

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


@app.route('/tilt/<degrees>', methods=['POST'])
def tilt(degrees: str):
  print("tilt request: ", degrees)
  try:
    num_degrees = int(degrees)
  except ValueError:
    abort(400, 'Invalid number of degrees: ' + degrees)
  kinect_service.do_tilt(num_degrees)
  return jsonify({'moved': True})


@app.route('/set-led-mode/<mode>', methods=['POST'])
def set_led_mode(mode: str):
  print("led mode request: ", mode)
  try:
    num_mode = int(mode)
    assert 0 <= num_mode < 6, "mode must be between 0 and 5"
  except ValueError:
    abort(400, 'Invalid mode: ' + mode)
  kinect_service.set_led_mode(num_mode)
  return jsonify({'changed_led': True})


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
  base64_string = np_img_to_base64(np_array)
  return jsonify(dict(image=base64_string))


@app.route('/current-depth-view', methods=['GET'])
def current_depth_view():
    print("current-depth-view request")
    sensory_output = depth_camera_module.build_subconscious_input(context)
    raw_depth_arr = sensory_output['last_depth_frame']

    # Normalize the depth image to range 0-255
    normalized_depth = (raw_depth_arr / 2.048 * 255).astype(np.uint8)
    print(f'normalized_depth: shape={normalized_depth.shape}, min={normalized_depth.min()}, max={normalized_depth.max()}')
    depth_colored = cv2.applyColorMap(normalized_depth, cv2.COLORMAP_TURBO)
    
    # Convert numpy image to base64 for transmission
    def np_img_to_base64(img):
      # Convert from RGB to BGR
      img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
      # Encode the image in PNG format
      _, buffer = cv2.imencode('.png', img_bgr)
      # Convert the buffer to a base64 string
      return base64.b64encode(buffer).decode('utf-8')

    base64_string = np_img_to_base64(depth_colored)

    # Compress and serialize raw image
    serialized_array = pickle.dumps(raw_depth_arr)
    compressed_array = zlib.compress(serialized_array)
    encoded_string = base64.b64encode(compressed_array).decode('utf-8')

    return jsonify(dict(image=base64_string, raw_image=encoded_string))

@app.route('/current-labeled-view', methods=['GET'])
def current_labeled_view():
  print("current_labeled_view request")
  depth_sensory_output = depth_camera_module.build_subconscious_input(context)
  depth_camera_arr: np.array = depth_sensory_output['last_depth_frame']
  
  camera_sensory_output = camera_module.build_subconscious_input(context)
  camera_arr: np.array = camera_sensory_output['last_frame']
  
  labeled_img, xs_info = label_passageways(camera_arr, depth_camera_arr)
  base64_image = add_horizontal_guide_encode(labeled_img)
  
  return jsonify(dict(image=base64_image))


@app.route('/helloworld', methods=['GET'])
def hello_world():
  return 'Hello World'


@app.route('/command', methods=['POST'])
def command():
  # Parse JSON data from the request
  data = request.get_json()
  if not data:
    return jsonify({'error': 'No JSON data provided'}), 400
  
  # Extract user_input and reasoning from the JSON body
  user_input = data.get('user_input')
  reasoning = data.get('reasoning')
  
  # Check if necessary data is present
  if user_input is None or reasoning is None:
    return jsonify({'error': 'Missing data in request'}), 400
  
  result = executor.execute(
    context=context,
    new_task=TaskDefinition(input=user_input, reasoning=reasoning, task=user_input)
  )
  
  return jsonify(result)


if __name__ == '__main__':
  print('starting manual control server')
  app.run(debug=False, port=5001, host='0.0.0.0')
