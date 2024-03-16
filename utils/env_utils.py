import os


def check_env_flag(env_var: str) -> bool:
  val = os.environ.get(env_var)
  return val is not None and val.lower() == 'true'
