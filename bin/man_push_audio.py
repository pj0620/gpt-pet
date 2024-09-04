import os
import sys
from datetime import datetime

from firebase_admin import credentials, db, initialize_app
from dotenv import load_dotenv


def get_env_var(env_var: str) -> str:
  val = os.environ.get(env_var)
  if val is None:
    raise Exception(f'environment variable {env_var} is not set')
  return val


load_dotenv()
database_url = get_env_var('FIREBASE_DATABASE_URL')
cred_obj = credentials.Certificate(get_env_var('FIREBASE_CERT_PATH'))
initialize_app(cred_obj, {
  'databaseURL': database_url
})
ref = db.reference("/")

if len(sys.argv) != 2:
  print("invalid arguments")
  print(f"Usage: {sys.argv} \"<audio to send to gptpet>\"")
  exit(0)

new_command = sys.argv[1]

timestamp = datetime.utcnow().isoformat()
ref.set({
  'command': new_command,
  'timestamp': str(timestamp)
  
})
