from abc import ABC, abstractmethod


class BaseTiltService(ABC):
  
  @abstractmethod
  def do_tilt(self, degrees: int) -> None:
    """
    Tilts GPTPet
    :param degrees: degrees to tile
    :return: None
    """
    pass
