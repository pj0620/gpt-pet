from model.collision import StuckError
from model.motor import MovementResult
from service.analytics_service import AnalyticsService
from service.motor.base_motor_service import BaseMotorService


class StuckMotorService(BaseMotorService):
  def __init__(self, analytics_service: AnalyticsService):
    self.analytics_service = analytics_service
  
  def do_movement(self, action: str, move_magnitude: float = None) -> MovementResult:
    self.analytics_service.new_text("[StuckMotorService] do_movement called, throwing fake stuck error")
    error_msg = f"Stuck error: depth sensor measurements indicate that you are stuck."
    self.analytics_service.new_text(error_msg + f"; before: {3.14}, after: {3.14}")
    raise StuckError(error_msg)
  
  def do_rotate(self, action: str, degrees: float = None) -> MovementResult:
    self.analytics_service.new_text("[StuckMotorService] do_rotate called, throwing fake stuck error")
    error_msg = f"Stuck error: depth sensor measurements indicate that you are stuck."
    self.analytics_service.new_text(error_msg + f"; before: {3.14}, after: {3.14}")
    raise StuckError(error_msg)
  
  def stop(self):
    self.analytics_service.new_text("[StuckMotorService] stop called")
  
  def setup_motors(self):
    self.analytics_service.new_text("[StuckMotorService] setup_motors called")
