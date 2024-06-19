import select
import sys
import threading
import time

from gptpet_context import GPTPetContext
from model.subconscious import ConsciousInput
from module.subconscious.input.base_subconscious_input_module import BaseSubconsciousInputModule

AUDIO_MODULE_SCHEMA = {
  "heard_text": "text of audio gptpet heard from its microphone"
}
AUDIO_MODULE_DESCRIPTION = "Capture of text GPTPet heard from its microphone as text"
AUDIO_MODULE_NAME = "audio_module"


class StdinAudioModule(BaseSubconsciousInputModule):
  def build_conscious_input(self, context: GPTPetContext) -> ConsciousInput:
    heard_text = input("Enter text for GPTPet to hear: ")
    print(f"Sending following audio to GPTPet `{heard_text}`")
    
    return ConsciousInput(
      value=dict(heard_text=heard_text),
      schema=AUDIO_MODULE_SCHEMA,
      description=AUDIO_MODULE_DESCRIPTION,
      name=AUDIO_MODULE_NAME
    )
