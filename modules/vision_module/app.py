import sys

from flasgger import Swagger, swag_from
from flask import Flask, request, jsonify
import logging

from services.vision_service import VisionService
from utils.logging_utils import log_function_call

app = Flask(__name__)

swagger_config = {
  "headers": [
    ('Access-Control-Allow-Origin', '*'),
    ('Access-Control-Allow-Methods', "GET, POST"),
  ],
  "specs": [
    {
      "endpoint": 'Vision_Module',
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

# Create a logger object
logger = logging.getLogger('vision_module')
logger.setLevel(logging.INFO)  # Set the logging level

# Create a handler that outputs log messages to stdout
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.INFO)  # Set the logging level for the handler

# Create a formatter and set it for the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stdout_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(stdout_handler)

vision_service = VisionService()


@log_function_call
@swag_from("docs/describe_room.yaml")
@app.route("/describe-room", methods=['POST'])
def describe_room():
  data = request.get_json()
  if not data or 'image' not in data:
    return jsonify({"error": "No image provided"}), 400
  
  img_b64 = data['image']
  
  try:
    description = vision_service.describe_room(img_b64)
    print(f"{description=}")
    return jsonify(description), 200
  except Exception as e:
    print(e)
    return jsonify({"error": "Invalid image format or internal error"}), 500


if __name__ == "__main__":
  app.run(debug=True)
