from abc import ABC


class BaseLEDService(ABC):
  def set_led_mode(self, led_mode: int) -> None:
    """
    sets led based on kinect led modes
    TODO: create more general way to do this
    :param led_mode: led mode from kinect
    :return: None
    """
    pass
