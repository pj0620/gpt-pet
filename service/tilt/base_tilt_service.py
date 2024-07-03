from abc import ABC


class BaseTiltService(ABC):
  def do_tilt(self, degrees: int) -> None:
    """
    Tilts GPTPet
    :param degrees: degrees to tile
    :return: None
    """
    pass