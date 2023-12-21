import base64

import requests


class VisionService:
    def __init__(self, environment_module_url):
        self.environment_module_url = environment_module_url

    def capture_room_view(self):
        print(f'getting capture of current view from {self.environment_module_url}/capture-image')
        # Make a GET request to fetch the image
        response = requests.get(self.environment_module_url + '/capture-image')

        # Check if the request was successful
        if response.status_code != 200:
            raise Exception(f"Cannot connect to self.environment_module_url at "
                            f"{self.environment_module_url}/capture-image, "
                            f"recieved {response.status_code} response code")

        #
        encoded_image = base64.b64encode(response.content).decode('utf-8')
