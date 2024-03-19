import numpy as np
import requests

from utils.env_utils import get_env_var
from utils.prompt_utils import encode_image_array


class AnalyticsService:
  def __init__(self):
    self.base_url = get_env_var('ANALYTICS_SERVER_ENDPOINT')
  
  def _make_request(self, endpoint: str, data=None):
    """
    A shared method to make POST requests to the analytics server.
    :param endpoint: The API endpoint (e.g., '/text', '/image')
    :param data: The JSON payload for the request
    :param files: The files payload for the request
    :return: Response from the server or error message
    """
    url = f"{self.base_url}{endpoint}"
    try:
      response = requests.post(url, json=data, timeout=5)  # 5 seconds timeout
      response.raise_for_status()  # Raises an HTTPError if the response was an error
      return response.json()
    except requests.ConnectionError:
      print('Connection error. Unable to connect to the analytics server.')
    except requests.Timeout:
      print('Request timed out. The analytics server did not respond in time.')
    except requests.RequestException as e:
      print(f'An error occurred:', e)
  
  def new_text(self, text: str):
    """
    Logs text to the analytics server.
    :param text: Text to log
    :return: Response from the analytics server or error message
    """
    payload = {'text': text}
    self._make_request('/text', data=payload)
  
  def new_image(self, image: str):
    """
    Logs a base64-encoded image to the analytics server.
    :param image: Base64-encoded image to log
    :return: Response from the analytics server or error message
    """
    payload = {'image': f'data:image/jpeg;base64,{image}' }
    self._make_request('/image', data=payload)
    
  def new_image_from_arr(self, image_arr: np.array):
    """
    Logs a numpy array image to the analytics server.
    :param image_arr: image array to log
    :return: Response from the analytics server or error message
    """
    self.new_image(encode_image_array(image_arr))