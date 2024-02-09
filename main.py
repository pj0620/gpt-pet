from gptpet import GPTPet
from gptpet_env import GPTPetEnv
from module.sensory.ai2thor_camera_module import Ai2ThorCameraModule
from module.sensory.base_sensory_module import BaseSensoryModule
from module.subconcious.base_subconscious_module import BaseSubconsciousModule
from module.subconcious.vision_module import VisionModule
from service.vectordb_adapter_service import VectorDBAdapterService
from sim_adapter import SimAdapter

test_env = 'local'

env = GPTPetEnv()

# setup vectordb
env.vectordb_adapter_service = VectorDBAdapterService()

sensory_modules: list[BaseSensoryModule] = []
if test_env == 'local':
  sim_adapter = SimAdapter()
  sensory_modules = [
    Ai2ThorCameraModule(sim_adapter)
  ]
else:
  sensory_modules = []

subconscious_modules: list[BaseSubconsciousModule] = [
  VisionModule()
]

gptpet = GPTPet(
  sensory_modules=sensory_modules,
  subconscious_modules=subconscious_modules
)

gptpet.exist(env)
