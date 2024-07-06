from gptpet_context import GPTPetContext
from module.sensory.base_sensory_module import BaseSensoryModule
from module.sensory.sim.ai2thor_camera_module import Ai2ThorCameraModule
from module.sensory.sim.ai2thor_depth_camera_module import Ai2ThorDepthCameraModule
from service.analytics_service import AnalyticsService
from service.device_io.sim.ai2thor_device_io_adapter import Ai2thorDeviceIOAdapter
from service.kinect.sim.noop_kinect_service import NoopKinectService
from service.motor.sim.ai2thor_motor_service import Ai2ThorMotorService
from service.sim_adapter import SimAdapter
from service.vectordb_adapter_service import VectorDBAdapterService
from service.visual_llm_adapter_service import VisualLLMAdapterService
from utils.env_utils import get_env


def build_context() -> tuple[GPTPetContext, list[BaseSensoryModule]]:
  context = GPTPetContext()
  context.analytics_service = AnalyticsService()
  context.vectordb_adapter = VectorDBAdapterService(context.analytics_service)
  context.visual_llm_adapter = VisualLLMAdapterService()
  
  if get_env() == 'local':
    sim_adapter = SimAdapter()
    context.motor_adapter = Ai2ThorMotorService(sim_adapter)
    camera_module = Ai2ThorCameraModule(sim_adapter)
    depth_camera_module = Ai2ThorDepthCameraModule(sim_adapter)
    context.kinect_service = NoopKinectService()
    context.device_io_adapter = Ai2thorDeviceIOAdapter(sim_adapter)
  else:
    # keep imports here to avoid GPIO libraries causing issues
    from service.motor.physical.physical_motor_service import PhysicalMotorService
    from service.device_io.physical.physical_device_io_adapter import PhysicalDeviceIOAdapter
    from service.kinect.physical.async_physical_kinect_service import AsyncPhysicalKinectService
    from module.sensory.physical.async_physical_camera_module import AsyncPhysicalCameraModule
    from module.sensory.physical.async_physical_depth_camera_module import AsyncPhysicalDepthCameraModule
    
    print('setting up device_io_adapter')
    context.device_io_adapter = PhysicalDeviceIOAdapter()
    
    print('setting up AsyncPhysicalKinectService')
    context.kinect_service = AsyncPhysicalKinectService()
    
    print('setting up camera/depth camera modules')
    camera_module = AsyncPhysicalCameraModule(context.kinect_service)
    depth_camera_module = AsyncPhysicalDepthCameraModule(context.kinect_service)
    
    print('setting up motor adapter')
    context.motor_adapter = PhysicalMotorService(
      kinect_service=context.kinect_service,
      device_io_adapter=context.device_io_adapter,
      analytics_service=context.analytics_service
    )
  # see manual.py before changing this ordering
  sensory_modules = [camera_module, depth_camera_module]
  return context, sensory_modules
