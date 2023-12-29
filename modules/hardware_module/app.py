import base64
import logging
import os
import sys
import io
from PIL import Image

from flask_cors import CORS
from flask import Flask, request, send_file
from flasgger import Swagger, swag_from

from constants.endpoint_constants import INVALID_DIRECTION_ERROR_MESSAGE, \
  VALID_MOVE_DIRECTIONS, INVALID_DEGREES_ERROR_MESSAGE
from service.Ai2ThorService import Ai2ThorService
from util.logging_utils import log_function_call
from util.type_utils import is_valid_integer
from flask import send_from_directory

app = Flask(__name__)

swagger_config = {
  "headers": [
    ('Access-Control-Allow-Origin', '*'),
    ('Access-Control-Allow-Methods', "GET, POST"),
  ],
  "specs": [
    {
      "endpoint": 'Hardware_Module',
      "route": '/swagger.json',
      "rule_filter": lambda rule: True,
      "model_filter": lambda tag: True,
    }
  ],
  "static_url_path": "/flasgger_static",
  "swagger_ui": True,
  "specs_route": "/apidocs/",
  
}
swagger = Swagger(app, config=swagger_config)
CORS(app, supports_credentials=True)  # This will disable CORS for all routes

ai2ThorService = Ai2ThorService()

# Create a logger object
logger = logging.getLogger('hardware_module')
logger.setLevel(logging.INFO)  # Set the logging level

# Create a handler that outputs log messages to stdout
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.INFO)  # Set the logging level for the handler

# Create a formatter and set it for the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stdout_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(stdout_handler)


@app.route('/favicon.ico')
def favicon():
  return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico',
                             mimetype='image/vnd.microsoft.icon')


@app.before_request
def log_request_info():
  data = request.get_data(as_text=True) if request.method == 'POST' else 'No data'
  logger.info(f'Request: {request.url} - {request.method} - Data: {data}')


@app.after_request
def log_response_info(response):
  if request.path == '/capture-image':
    app.logger.info("Response for /capture-image, not logging data.")
    return response
  
  if not response.direct_passthrough:
    if response.mimetype != 'image/jpeg':  # Check if the response is not an image
      response_data = response.get_data(as_text=True)
      logger.info(f'Response: {response.status_code} - Data: {response_data}')
    else:
      app.logger.info("Response is an image, not logging data.")
  else:
    app.logger.info("Response is a direct passthrough, not logging data.")
  return response


@log_function_call
@swag_from("docs/move.yaml")
@app.route("/move", methods=['POST'])
def move():
  direction = request.args.get('direction')
  logger.info(f'new move request: {direction=}')
  
  if direction not in VALID_MOVE_DIRECTIONS:
    msg = INVALID_DIRECTION_ERROR_MESSAGE.format(direction, VALID_MOVE_DIRECTIONS)
    return msg, 400
  
  sucessful = ai2ThorService.move(direction)
  if sucessful:
    return f'successfully moved {direction=}', 200
  else:
    return f'error while moving {direction=}', 409


@log_function_call
@swag_from("docs/turn.yaml")
@app.route("/turn", methods=['POST'])
def turn():
  degrees = request.args.get('degrees')
  logger.info(f'new turn request of {degrees} degrees')
  
  if not is_valid_integer(degrees):
    msg = INVALID_DEGREES_ERROR_MESSAGE.format(degrees)
    return msg, 400
  
  successful = ai2ThorService.turn(int(degrees))
  if successful:
    return f'successfully turned {degrees} degrees', 200
  else:
    return f'error while turning {degrees} degrees', 409


@log_function_call
@swag_from("docs/capture_image.yaml")
@app.route("/capture-image", methods=['GET'])
def capture_image():
  arr = ai2ThorService.get_last_image_np()
  img = Image.fromarray(arr)
  
  # Save image to a BytesIO object
  img_io = io.BytesIO()
  img.save(img_io, 'JPEG')  # You can change 'JPEG' to 'PNG' if you prefer
  img_io.seek(0)
  
  # Encode the image data in base64
  img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
  
  # Return the base64 encoded string
  return img_base64


if __name__ == '__main__':
  app.run(debug=True, port=int(os.environ['ENV_MODULE_PORT']))
