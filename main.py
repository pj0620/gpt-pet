import numpy as np

from constants.kinect import FREENECT_LED_YELLOW, FREENECT_LED_RED
from gptpet import GPTPet
from gptpet_context import GPTPetContext
from mixin.goal.simple_chain_goal_mixin import SimpleChainGoalMixin
from module.conscious.goal_aware_chain_conscious_module import GoalAwareChainConsciousModule
from module.sensory.proximity_module import ProximityModule
from module.sensory.sim.ai2thor_camera_module import Ai2ThorCameraModule
from module.sensory.sim.ai2thor_depth_camera_module import Ai2ThorDepthCameraModule
from module.subconscious.input.base_subconscious_input_module import BaseSubconsciousInputModule
from module.subconscious.input.proximiy_sensor_module import ProximitySensorModule
from module.subconscious.input.stdin_speech_module import StdinAudioModule
from module.subconscious.input.vision_module_with_goals import VisionModuleWithGoals
from module.subconscious.output.single_input_agent_executor_module import SingleInputAgentExecutorModule
from service.analytics_service import AnalyticsService
from service.device_io.sim.ai2thor_device_io_adapter import Ai2thorDeviceIOAdapter
from service.motor.sim.ai2thor_motor_service import Ai2ThorMotorService
from service.sim_adapter import SimAdapter
from service.kinect.sim.noop_kinect_service import NoopKinectService
from service.vectordb_adapter_service import VectorDBAdapterService
from service.visual_llm_adapter_service import VisualLLMAdapterService
from utils.build_context import build_context
from utils.env_utils import get_env_var, check_env_flag

np.set_printoptions(precision=3, suppress=True)

context, sensory_modules = build_context()

context.kinect_service.set_led_mode(FREENECT_LED_RED)
context.kinect_service.do_tilt(0)

context.analytics_service.new_text("initializing proximity module")
sensory_modules.append(ProximityModule(context.device_io_adapter))

context.analytics_service.new_text("initializing vision module")
subconscious_input_modules: list[BaseSubconsciousInputModule] = [
  VisionModuleWithGoals(context.vectordb_adapter)
]

if check_env_flag('MANUAL_AUDIO_INPUT'):
  subconscious_input_modules.append(StdinAudioModule())

if not check_env_flag('SIM_SKIP_PROXIMITY_SENSOR'):
  context.analytics_service.new_text("initializing subconscious proximity sensor module")
  subconscious_input_modules.append(ProximitySensorModule())

context.analytics_service.new_text("initializing conscious module")
conscious_module = GoalAwareChainConsciousModule()

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
