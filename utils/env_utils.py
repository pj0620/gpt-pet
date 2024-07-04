import argparse
import os
import subprocess
import socket


def check_env_flag(env_var: str) -> bool:
  val = os.environ.get(env_var)
  return val is not None and val.lower() == 'true'

def get_env_var(env_var: str) -> str:
  val = os.environ.get(env_var)
  if val is None:
    raise Exception(f'environment variable {env_var} is not set')
  return val

def check_if_process_running(process_search: str) -> bool:
  # Define the command to check for the process
  command = f"pgrep -l -a -f manual.py"
  
  # Run the command
  result = subprocess.run(command, shell=True, text=True, capture_output=True)
  is_running_process = bool(result.stdout)
  if is_running_process:
    print("process already running: stdout = ")
    print(result.stdout)
  
  # Check if the output is non-empty
  return is_running_process
  
def check_port_in_use(host, port):
  """
  Check if a port is in use on a specified host.

  Args:
  host (str): The hostname or IP address to check.
  port (int): The port number to check.

  Returns:
  bool: True if the port is in use, False otherwise.
  """
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
      s.bind((host, port))
      return False  # The port is available
    except socket.error as e:
      return True  # The port is in use
  
  
def get_env():
  parser = argparse.ArgumentParser(description="GPTPet Environment")
  parser.add_argument(
      '--env', '-e',
      choices=['local', 'physical'],
      required=True,
      help='Specify the environment: local or physical'
  )
  args = parser.parse_args()
  return args.env
  