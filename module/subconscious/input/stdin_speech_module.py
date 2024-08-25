import select
import sys
import threading
import time

from constants.audio import AUDIO_MODULE_SCHEMA, AUDIO_MODULE_DESCRIPTION, AUDIO_MODULE_NAME, AUDIO_CONSCIOUS_KEY
from gptpet_context import GPTPetContext
from model.subconscious import ConsciousInput
from module.subconscious.input.base_subconscious_input_module import BaseSubconsciousInputModule

class StdinAudioModule(BaseSubconsciousInputModule):
  def build_conscious_input(self, context: GPTPetContext) -> ConsciousInput:
    heard_text = input("Enter text for GPTPet to hear: ")
    print(f"Sending following audio to GPTPet `{heard_text}`")
    return ConsciousInput(
      value={AUDIO_CONSCIOUS_KEY: heard_text},
      schema=AUDIO_MODULE_SCHEMA,
      description=AUDIO_MODULE_DESCRIPTION,
      name=AUDIO_MODULE_NAME
    )
 