import json
import os
import sys

from openai import OpenAI
from flasgger import Swagger, swag_from
from flask import Flask, request, jsonify
import logging
from flask_cors import CORS

from chat.ChatAgent import ChatAgent
from util.logging_utils import log_function_call

app = Flask(__name__)

swagger_config = {
    "headers": [
        ('Access-Control-Allow-Origin', '*'),
        ('Access-Control-Allow-Methods', "GET, POST"),
    ],
    "specs": [
        {
            "endpoint": 'Vision_Proxy_Module',
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

# Create a logger object
logger = logging.getLogger('vision_proxy_module')
logger.setLevel(logging.INFO)  # Set the logging level

# Create a handler that outputs log messages to stdout
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.INFO)  # Set the logging level for the handler

# Create a formatter and set it for the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stdout_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(stdout_handler)

room_capture_agent = ChatAgent(
    role=''
)

@log_function_call
@swag_from("docs/analyze-text-image.yaml")
@app.route("/analyze-text-image", methods=['GET'])
def capture_room_view():
    input_body = json.loads(request.data)



    return json.dumps({"responseText": "dummy"}), 200


if __name__ == '__main__':
    app.run(debug=True, port=int(os.environ['VISION_PROXY_MODULE_PORT']))
