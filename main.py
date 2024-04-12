import os

import numpy as np

from gptpet import GPTPet
from gptpet_context import GPTPetContext
from module.conscious.agent_conscious_module import AgentConsciousModule
from module.sensory.sim.ai2thor_camera_module import Ai2ThorCameraModule
from module.sensory.sim.ai2thor_depth_camera_module import Ai2ThorDepthCameraModule
from module.sensory.sim.ai2thor_proximity_module import Ai2ThorProximityModule
from module.subconscious.input.base_subconscious_input_module import BaseSubconsciousInputModule
from module.subconscious.input.proximiy_sensor_module import ProximitySensorModule
from module.subconscious.input.vision_module import VisionModule
from module.subconscious.output.single_input_agent_executor_module import SingleInputAgentExecutorModule
from service.analytics_service import AnalyticsService
from service.motor.sim.ai2thor_motor_adapter import Ai2ThorMotorService
from service.sensor.sim.ai2thor_proximity_sensor_adapter import Ai2thorProximitySensorAdapter
from service.sim_adapter import SimAdapter
from service.vectordb_adapter_service import VectorDBAdapterService
from service.visual_llm_adapter_service import VisualLLMAdapterService

np.set_printoptions(precision=3, suppress=True)

# TODO: request param
test_env = 'local'

context = GPTPetContext()

# setup vectordb
context.vectordb_adapter = VectorDBAdapterService()
context.visual_llm_adapter = VisualLLMAdapterService()
context.analytics_service = AnalyticsService()

if test_env == 'local':
  sim_adapter = SimAdapter()
  context.motor_adapter = Ai2ThorMotorService(sim_adapter)
  context.proximity_sensor_adapter = Ai2thorProximitySensorAdapter(sim_adapter)
  sensory_modules = [
    Ai2ThorCameraModule(sim_adapter),
    Ai2ThorDepthCameraModule(sim_adapter),
    Ai2ThorProximityModule(sim_adapter)
  ]
else:
  sensory_modules = []

subconscious_input_modules: list[BaseSubconsciousInputModule] = [
  VisionModule(context.vectordb_adapter)
]

if os.environ.get('SIM_SKIP_PROXIMITY_SENSOR') != 'true':
  subconscious_input_modules.append(ProximitySensorModule())

gptpet = GPTPet(
  # collects raw sensor data
  sensory_modules=sensory_modules,
  
  # builds text input from sensor data
  subconscious_input_modules=subconscious_input_modules,
  
  # use text input to create task
  conscious_module=AgentConsciousModule(),
  
  # executes task
  executor_module=SingleInputAgentExecutorModule(context)
)

gptpet.exist(context)
