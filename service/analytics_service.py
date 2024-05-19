import asyncio
import concurrent.futures

import aiohttp
import numpy as np
import requests

from utils.env_utils import get_env_var
from utils.prompt_utils import encode_image_array


class AnalyticsService:
  def __init__(self):
    self.base_url = get_env_var('ANALYTICS_SERVER_ENDPOINT')
    self.loop = asyncio.get_event_loop()
    self.executor = concurrent.futures.ThreadPoolExecutor()
  
  async def _make_request(self, endpoint: str, data=None):
    """
    A shared method to make POST requests to the analytics server asynchronously.
    :param endpoint: The API endpoint (e.g., '/text', '/image')
    :param data: The JSON payload for the request
    :return: Response from the server or error message
    """
    url = f"{self.base_url}{endpoint}"
    async with aiohttp.ClientSession() as session:
      try:
        async with session.post(url, json=data, timeout=5) as response:
          response.raise_for_status()  # Raises an HTTPError if the response was an error
          return await response.json()
      except aiohttp.ClientConnectionError as e:
        print('Connection error. Unable to connect to the analytics server.', e)
      except asyncio.TimeoutError as e:
        print('Request timed out. The analytics server did not respond in time.', e)
      except aiohttp.ClientError as e:
        print(f'An error occurred:', e)
  
  def new_text(self, text: str):
    """
    Logs text to the analytics server.
    :param text: Text to log
    :return: Response from the analytics server or error message
    """
    payload = {'text': text}
    print(text)
    return self.loop.run_in_executor(self.executor, asyncio.run, self._make_request('/text', data=payload))
  
  def new_image(self, image: str):
    """
    Logs a base64-encoded image to the analytics server.
    :param image: Base64-encoded image to log
    :return: Response from the analytics server or error message
    """
    payload = {'image': f'data:image/jpeg;base64,{image}'}
    return self.loop.run_in_executor(self.executor, asyncio.run, self._make_request('/image', data=payload))
  
  def new_image_from_arr(self, image_arr: np.array):
    """
    Logs a numpy array image to the analytics server.
    :param image_arr: image array to log
    :return: Response from the analytics server or error message
    """
    image = encode_image_array(image_arr)
    return self.new_image(image)