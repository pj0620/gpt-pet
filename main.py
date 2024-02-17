from gptpet import GPTPet
from gptpet_env import GPTPetEnv
from module.conscious.dummy_conscious_module import DummyConsciousModule
from module.conscious.walk_forward_module import WalkForwardModule
from module.sensory.ai2thor_camera_module import Ai2ThorCameraModule
from module.subconscious.input.base_subconscious_input_module import BaseSubconsciousInputModule
from module.subconscious.input.vision_module import VisionModule

from module.subconscious.output.agent_executor_module import AgentExecutorModule
from module.subconscious.output.noop_executor_module import DummyExecutorModule
from service.motor.ai2thor_motor_service import Ai2ThorMotorService
from service.sim_adapter import SimAdapter
from service.vectordb_adapter_service import VectorDBAdapterService
from service.visual_llm_adapter_service import VisualLLMAdapterService

import numpy as np

np.set_printoptions(precision=3, suppress=True)

# TODO: request param
test_env = 'local'

env = GPTPetEnv()

# setup vectordb
env.vectordb_adapter = VectorDBAdapterService()
env.visual_llm_adapter = VisualLLMAdapterService()

if test_env == 'local':
  sim_adapter = SimAdapter()
  sensory_modules = [
    Ai2ThorCameraModule(sim_adapter)
  ]
  env.motor_service = Ai2ThorMotorService(sim_adapter)
else:
  sensory_modules = []

subconscious_input_modules: list[BaseSubconsciousInputModule] = [
  VisionModule()
]

gptpet = GPTPet(
  sensory_modules=sensory_modules,
  subconscious_input_modules=subconscious_input_modules,
  conscious_module=WalkForwardModule(),
  executor_module=DummyExecutorModule()
)

gptpet.exist(env)
