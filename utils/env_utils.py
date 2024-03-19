import os


def check_env_flag(env_var: str) -> bool:
  val = os.environ.get(env_var)
  return val is not None and val.lower() == 'true'

def get_env_var(env_var: str) -> str:
  val = os.environ.get(env_var)
  if val is None:
    raise Exception(f'environment variable {env_var} is not set')
  return val
  