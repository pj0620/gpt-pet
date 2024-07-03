from service.tilt.base_tilt_service import BaseTiltService
import freenect


class PhysicalTiltService(BaseTiltService):
  def do_tilt(self, degrees: int) -> None:
    """Set the tilt angle of the Kinect sensor."""
    # The angle should be in the range of -30 to 30 degrees
    if -30 <= degrees <= 30:
      freenect.set_tilt_degs(freenect.sync_get_device(), degrees)
      print(f"Tilt angle set to {degrees} degrees")
    else:
      print("Angle out of range. Please enter an angle between -30 and 30 degrees.")
