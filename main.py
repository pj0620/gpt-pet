from gptpet import GPTPet
from gptpet_context import GPTPetContext
from module.conscious.agent_conscious_module import AgentConsciousModule
from module.conscious.dummy_conscious_module import DummyConsciousModule
from module.conscious.walk_forward_module import WalkForwardModule
from module.sensory.ai2thor_camera_module import Ai2ThorCameraModule
from module.subconscious.input.base_subconscious_input_module import BaseSubconsciousInputModule
from module.subconscious.input.proximiy_sensor_module import ProximitySensorModule
from module.subconscious.input.vision_module import VisionModule

from module.subconscious.output.agent_executor_module import AgentExecutorModule
from module.subconscious.output.noop_executor_module import DummyExecutorModule
from module.subconscious.output.single_input_agent_executor_module import SingleInputAgentExecutorModule
from service.motor.ai2thor_motor_adapter import Ai2ThorMotorService
from service.sensor.ai2thor_proximity_sensor_adapter import Ai2thorProximitySensorAdapter
from service.sim_adapter import SimAdapter
from service.vectordb_adapter_service import VectorDBAdapterService

import numpy as np

from service.vision_llm.blip_visual_llm_adapter_service import BlipVisualLLMAdapterService

np.set_printoptions(precision=3, suppress=True)

# TODO: request param
test_env = 'local'

context = GPTPetContext()

# setup vectordb
context.vectordb_adapter = VectorDBAdapterService()
context.visual_llm_adapter = BlipVisualLLMAdapterService()

if test_env == 'local':
  sim_adapter = SimAdapter()
  context.motor_adapter = Ai2ThorMotorService(sim_adapter)
  context.proximity_sensor_adapter = Ai2thorProximitySensorAdapter(sim_adapter)
  sensory_modules = [
    Ai2ThorCameraModule(sim_adapter)
  ]
else:
  sensory_modules = []

subconscious_input_modules: list[BaseSubconsciousInputModule] = [
  VisionModule(),
  ProximitySensorModule()
]

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
