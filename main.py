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

context = GPTPetContext()

context.analytics_service = AnalyticsService()
context.analytics_service.new_text("finished initializing analytics")

# setup vectordb
context.analytics_service.new_text("initializing vectordb adapter")
context.vectordb_adapter = VectorDBAdapterService(context.analytics_service)

context.analytics_service.new_text("initializing vision llm adapter")
context.visual_llm_adapter = VisualLLMAdapterService()
context.goal_mixin = SimpleChainGoalMixin(context.analytics_service, context.vectordb_adapter)

# gptpet_env = get_env_var('GPTPET_ENV')
# if gptpet_env == 'local':
#   sim_adapter = SimAdapter()
#
#   context.analytics_service.new_text("initializing motor service")
#   context.kinect_service = NoopKinectService()
#   context.motor_adapter = Ai2ThorMotorService(sim_adapter)
#   context.led_tilt_service = NoopKinectService()
#
#   context.analytics_service.new_text("initializing camera/depth camera modules")
#   sensory_modules = [
#     Ai2ThorCameraModule(sim_adapter),
#     Ai2ThorDepthCameraModule(sim_adapter)
#   ]
#
#   context.analytics_service.new_text("initializing device io adapter")
#   context.device_io_adapter = Ai2thorDeviceIOAdapter(sim_adapter)
# elif gptpet_env == 'physical':
#   # keep imports here to avoid GPIO libraries causing issues
#   from service.motor.physical.physical_motor_service import PhysicalMotorService
#   from service.device_io.physical.physical_device_io_adapter import PhysicalDeviceIOAdapter
#   from service.kinect.physical.async_physical_kinect_service import AsyncPhysicalKinectService
#   from module.sensory.physical.async_physical_camera_module import AsyncPhysicalCameraModule
#   from module.sensory.physical.async_physical_depth_camera_module import AsyncPhysicalDepthCameraModule
#
#   context.analytics_service.new_text("initializing device io adapter")
#   context.device_io_adapter = PhysicalDeviceIOAdapter()
#
#   print('setting up AsyncPhysicalKinectService')
#   context.kinect_service = AsyncPhysicalKinectService()
#
#   context.analytics_service.new_text("initializing motor service")
#   context.motor_adapter = PhysicalMotorService(
#     context=context
#   )
#
#   context.analytics_service.new_text("initializing camera/depth camera modules")
#   sensory_modules = [
#     AsyncPhysicalCameraModule(context.kinect_service),
#     AsyncPhysicalDepthCameraModule(context.kinect_service)
#   ]
# else:
#   raise Exception(
#     f"invalid GPTPET_ENV environment value of `{gptpet_env}` must be in the list `{['local', 'physical']}`")

context, sensory_modules = build_context()

context.kinect_service.set_led_mode(FREENECT_LED_RED)

context.analytics_service.new_text("initializing proximity module")
sensory_modules.append(ProximityModule(context.device_io_adapter))

context.analytics_service.new_text("initializing vision module")
subconscious_input_modules: list[BaseSubconsciousInputModule] = [
  # VisionModule(context.vectordb_adapter)
  VisionModuleWithGoals(context.vectordb_adapter)
]

if check_env_flag('MANUAL_AUDIO_INPUT'):
  subconscious_input_modules.append(StdinAudioModule())

if not check_env_flag('SIM_SKIP_PROXIMITY_SENSOR'):
  context.analytics_service.new_text("initializing subconscious proximity sensor module")
  subconscious_input_modules.append(ProximitySensorModule())

context.analytics_service.new_text("initializing conscious module")
# conscious_module = GenerativeAgentConsciousModule(context.vectordb_adapter, context.analytics_service)
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
