from gptpet_context import GPTPetContext
from model.subconscious import ConsciousInput
from module.subconscious.input.base_subconscious_input_module import BaseSubconsciousInputModule
from firebase_admin import credentials, db, initialize_app

from utils.env_utils import get_env_var

AUDIO_MODULE_SCHEMA = {
  "heard_text": "text of audio gptpet heard from its microphone"
}
AUDIO_MODULE_DESCRIPTION = "Capture of text GPTPet heard from its microphone as text"
AUDIO_MODULE_NAME = "audio_module"


class FirebaseAudioModule(BaseSubconsciousInputModule):
  def __init__(self):
    database_url = get_env_var('FIREBASE_DATABASE_URL')
    cred_obj = credentials.Certificate(get_env_var('FIREBASE_CERT_PATH'))
    initialize_app(cred_obj, {
      'databaseURL': database_url
    })
    self._ref = db.reference("/")
    self._last_timestamp = self._get_timestamp_from_db()
    
  def _get_timestamp_from_db(self):
    return self._ref.get()['timestamp']
  
  def _get_command_from_db(self):
    return self._ref.get()['command']
  
  def build_conscious_input(self, context: GPTPetContext) -> ConsciousInput:
    command = ''
    
    cur_timestamp = self._get_timestamp_from_db()
    if cur_timestamp != self._last_timestamp:
      self._last_timestamp = cur_timestamp
      command = self._get_command_from_db()
      context.analytics_service.new_text(f'found new command to send to gptpet: "{command}"')
    
    return ConsciousInput(
      value=dict(heard_text=command),
      schema=AUDIO_MODULE_SCHEMA,
      description=AUDIO_MODULE_DESCRIPTION,
      name=AUDIO_MODULE_NAME
    )
