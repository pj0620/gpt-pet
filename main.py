from gptpet import GPTPet
from gptpet_env import GPTPetEnv
from module.conscious.walk_forward_module import WalkForwardModule
from module.conscious.base_conscious_module import BaseConsciousModule
from module.sensory.ai2thor_camera_module import Ai2ThorCameraModule
from module.subconscious.base_subconscious_module import BaseSubconsciousModule
from module.subconscious.vision_module import VisionModule
from service.motor.ai2thor_motor_service import Ai2ThorMotorService
from service.vectordb_adapter_service import VectorDBAdapterService
from service.visual_llm_adapter_service import VisualLLMAdapterService
from sim_adapter import SimAdapter

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

subconscious_modules: list[BaseSubconsciousModule] = [
  VisionModule()
]

conscious_modules: list[BaseConsciousModule] = [
  WalkForwardModule()
]

gptpet = GPTPet(
  sensory_modules=sensory_modules,
  subconscious_modules=subconscious_modules,
  conscious_modules=conscious_modules
)

gptpet.exist(env)
