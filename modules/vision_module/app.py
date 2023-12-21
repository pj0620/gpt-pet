import os
import sys

from flasgger import Swagger, swag_from
from flask import Flask
import logging
from flask_cors import CORS

from service.vision_service import VisionService
from util.logging_utils import log_function_call

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
# CORS(app, supports_credentials=True)  # This will disable CORS for all routes

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

environment_module_url = os.environ.get('ENVIRONMENT_MODULE_URL')
print(f'found {environment_module_url=}')
vision_service = VisionService(environment_module_url)


@log_function_call
@swag_from("docs/capture_room_view.yaml")
@app.route("/capture-room-view", methods=['PUT'])
def capture_room_view():
    vision_service.capture_room_view()
    return 'hello world'


if __name__ == "__main__":
    app.run(debug=True)
