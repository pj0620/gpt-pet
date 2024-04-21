import os
import subprocess


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
  
  