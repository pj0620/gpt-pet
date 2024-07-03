from service.tilt.base_tilt_service import BaseTiltService
import freenect


class PhysicalTiltService(BaseTiltService):
  def __init__(self):
    self.pending_tilt = False
  
  def body(self, dev, ctx, degrees):
    print(f"pending_tilt = {self.pending_tilt}")
    if self.pending_tilt:
      self.pending_tilt = False
    else:
      print('calling raise freenect.Kill')
      raise freenect.Kill
    print('calling set_tilt_degs')
    freenect.set_tilt_degs(dev, degrees)
  
  def do_tilt(self, degrees: int) -> None:
    """Set the tilt angle of the Kinect sensor."""
    # The angle should be in the range of -30 to 30 degrees
    if -30 <= degrees <= 30:
      # freenect.sync_stop()
      # ctx = freenect.init()
      # dev = freenect.open_device(ctx, freenect.num_devices(ctx) - 1)
      # freenect.set_tilt_degs(dev, degrees)
      print('calling stop sync')
      freenect.sync_stop()
      self.pending_tilt = True
      body_func = lambda dev, ctx: self.body(dev, ctx, degrees)
      print('calling runloop')
      freenect.runloop(body=body_func)
      print('calling stop sync')
      freenect.sync_stop()
      print(f"Tilt angle set to {degrees} degrees")
    else:
      print("Angle out of range. Please enter an angle between -30 and 30 degrees.")
