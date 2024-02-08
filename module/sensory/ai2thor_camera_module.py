from PIL import Image

from module.sensory.base_sensory_module import BaseSensoryModule
from sim_adapter import SimAdapter

class Ai2ThorCameraModule(BaseSensoryModule):
  def __init__(
      self,
      sim_adapter: SimAdapter
  ):
    self.sim_adapter = sim_adapter
    self.last_event = None
  
  def build_subconscious_input(self) -> None:
    last_frame_df = self.sim_adapter.get_view()
    
    im = Image.fromarray(last_frame_df)
    im.save("data/capture.jpeg")
