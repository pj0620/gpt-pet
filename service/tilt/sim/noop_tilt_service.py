from service.tilt.base_tilt_service import BaseTiltService


class NoopTiltService(BaseTiltService):
  def do_tilt(self, degrees: int) -> None:
    print(f'setting tilt to {degrees}')
