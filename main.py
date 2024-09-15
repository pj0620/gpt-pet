import numpy as np

from constants.kinect import FREENECT_LED_RED
from gptpet import GPTPet
from module.conscious.cached_conscious_module import CachedConsciousModule
from module.conscious.goal_aware_chain_conscious_module import GoalAwareChainConsciousModule
from module.conscious.goal_aware_gen_agent_conscious_module import GoalAwareGenAgentChainConsciousModule
from module.sensory.proximity_module import ProximityModule
from module.subconscious.input.base_subconscious_input_module import BaseSubconsciousInputModule
from module.subconscious.input.firebase_speech_module import FirebaseAudioModule
from module.subconscious.input.proximiy_sensor_module import ProximitySensorModule
from module.subconscious.input.stdin_speech_module import StdinAudioModule
from module.subconscious.input.vision_module_with_goals import VisionModuleWithGoals
from module.subconscious.output.single_input_agent_executor_module import SingleInputAgentExecutorModule
from utils.build_context import build_context
from utils.env_utils import check_env_flag

np.set_printoptions(precision=3, suppress=True)

context, sensory_modules = build_context()

context.kinect_service.set_led_mode(FREENECT_LED_RED)
context.kinect_service.do_tilt(-15)

context.analytics_service.new_text("initializing proximity module")
sensory_modules.append(ProximityModule(context.device_io_adapter))

context.analytics_service.new_text("initializing vision module")
subconscious_input_modules: list[BaseSubconsciousInputModule] = [
  VisionModuleWithGoals(context.vectordb_adapter)
]

# setup audio source
manual_audio_input: bool = check_env_flag('MANUAL_AUDIO_INPUT')
firebase_audio_input: bool = check_env_flag('FIREBASE_AUDIO_INPUT')
if manual_audio_input and firebase_audio_input:
  raise Exception('Cannot enable both MANUAL_AUDIO_INPUT, and FIREBASE_AUDIO_INPUT! Only one audio source can be used '
                  'at a time. Only set one of these environment variables to true.')
elif manual_audio_input:
  subconscious_input_modules.append(StdinAudioModule())
elif firebase_audio_input:
  subconscious_input_modules.append(FirebaseAudioModule())

if not check_env_flag('SIM_SKIP_PROXIMITY_SENSOR'):
  context.analytics_service.new_text("initializing subconscious proximity sensor module")
  subconscious_input_modules.append(ProximitySensorModule())

context.analytics_service.new_text("initializing conscious module")
conscious_module = CachedConsciousModule(GoalAwareGenAgentChainConsciousModule(
  vector_db_adapter_service=context.vectordb_adapter,
  analytics_service=context.analytics_service
))

context.analytics_service.new_text("initializing executor module")
executor_module = SingleInputAgentExecutorModule(context)

context.analytics_service.new_text("initializing GPTPet instance")
gptpet = GPTPet(
  # collects raw sensor data
  sensory_modules=sensory_modules,
  
  # builds text input from sensor data
  subconscious_input_modules=subconscious_input_modules,
  
  # use text input to create task
  conscious_module=conscious_module,
  
  # executes task
  executor_module=executor_module
)

context.analytics_service.new_text("beginning existence")
gptpet.exist(context)
